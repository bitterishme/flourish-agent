"""Flask blueprint: chat page and SSE streaming endpoint."""

from __future__ import annotations

import uuid

from flask import (
    Blueprint,
    Response,
    abort,
    render_template,
    request,
    session,
    stream_with_context,
)

from .client import stream_reply
from .prompt import build_system_prompt
from .skills import route_skills
from .storage import append_log, load_history

bp = Blueprint("flourish", __name__)


def _ensure_session() -> str:
    """Return the current session id, creating one if needed."""
    sid = session.get("session_id")
    if not sid:
        sid = uuid.uuid4().hex
        session["session_id"] = sid
    return sid


@bp.get("/")
def index():
    sid = _ensure_session()
    history = load_history(sid, limit=50)
    return render_template("chat.html", history=history)


@bp.post("/chat/send")
def chat_send():
    sid = _ensure_session()

    payload = request.get_json(silent=True) or {}
    message = (payload.get("message") or "").strip()
    if not message:
        abort(400, "empty message")

    append_log(sid, "user", message)
    history = load_history(sid, limit=20)
    triggered = route_skills(message, history)
    system = build_system_prompt(triggered)
    api_messages = [{"role": h["role"], "content": h["content"]} for h in history]

    collected: list[str] = []

    def generate():
        yield from stream_reply(system, api_messages, collected=collected)
        if collected and collected[0].strip():
            append_log(sid, "assistant", collected[0])

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@bp.post("/reset")
def reset():
    session.clear()
    return render_template("chat.html", history=[])

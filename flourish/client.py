"""Anthropic streaming client wrapper.

Yields Server-Sent Events (SSE) frames the Flask route hands to the browser.
Each text delta becomes one `data: {...}` line; the stream ends with
`data: [DONE]`. The full assistant text is also collected on a passed-in
list so the route handler can persist it to the log after streaming.
"""

from __future__ import annotations

import json
import os
from typing import Generator

import anthropic

MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 1500


def _sse(obj: dict) -> str:
    return "data: " + json.dumps(obj, ensure_ascii=False) + "\n\n"


def stream_reply(
    system: str,
    messages: list[dict],
    collected: list[str] | None = None,
) -> Generator[str, None, None]:
    """Stream a reply from Claude, yielding SSE-formatted strings.

    `messages` is a list of `{role, content}` dicts in Anthropic format.
    `collected` (optional): if provided, the full assistant text will be
    appended to this list once the stream completes — caller uses this to
    write the assistant turn to the log.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        yield _sse({
            "type": "error",
            "message": "ANTHROPIC_API_KEY is not set. Copy .env.example to .env and fill it in.",
        })
        yield "data: [DONE]\n\n"
        return

    client = anthropic.Anthropic(api_key=api_key)
    pieces: list[str] = []
    try:
        with client.messages.stream(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=system,
            messages=messages,
        ) as stream:
            for text in stream.text_stream:
                if not text:
                    continue
                pieces.append(text)
                yield _sse({"type": "delta", "text": text})
    except anthropic.APIError as e:
        yield _sse({"type": "error", "message": f"Anthropic API error: {e}"})
    except Exception as e:
        yield _sse({"type": "error", "message": f"Unexpected error: {e}"})
    finally:
        if collected is not None:
            collected.append("".join(pieces))
        yield "data: [DONE]\n\n"

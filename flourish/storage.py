"""Interaction log persistence (local JSONL files)."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOGS_DIR = ROOT / "logs"


def _log_path(sid: str) -> Path:
    return LOGS_DIR / f"{sid}.jsonl"


def append_log(sid: str, role: str, content: str) -> None:
    p = _log_path(sid)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps({"role": role, "content": content}, ensure_ascii=False) + "\n")


def load_history(sid: str, limit: int = 20) -> list[dict]:
    p = _log_path(sid)
    if not p.is_file():
        return []
    rows: list[dict] = []
    with p.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return rows[-limit:]

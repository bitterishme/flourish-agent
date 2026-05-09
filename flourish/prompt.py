"""Compose the system prompt for each turn from base + active skills."""

from __future__ import annotations

from pathlib import Path

from .skills import Skill, build_skill_block

ROOT = Path(__file__).resolve().parent.parent
PROMPTS_DIR = ROOT / "prompts"


def _read(name: str) -> str:
    p = PROMPTS_DIR / name
    if not p.is_file():
        return ""
    return p.read_text(encoding="utf-8").strip()


def build_system_prompt(triggered_skills: list[Skill]) -> str:
    parts = [_read("base-system.md")]
    skill_block = build_skill_block(triggered_skills)
    if skill_block:
        parts.append(skill_block)
    parts.append(_read("anti-patterns.md"))
    return "\n\n".join(p for p in parts if p)

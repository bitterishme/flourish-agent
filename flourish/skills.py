"""Load Claude Skills from disk and route user messages to them.

A skill is a directory under `skills/` containing a `SKILL.md` file with YAML
frontmatter (`name`, `description`, optional `triggers` list) and a markdown
body. The body is what gets injected into the system prompt when the skill is
active.

The router for v1 is intentionally simple: case-insensitive substring match
against each skill's `triggers` list. Returns at most 2 skills per turn.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

SKILLS_DIR = Path(__file__).resolve().parent.parent / ".claude" / "skills"


@dataclass(frozen=True)
class Skill:
    name: str
    description: str
    triggers: tuple[str, ...]
    body: str


_cache: dict[str, Skill] | None = None


def _parse_skill_md(text: str) -> tuple[dict, str]:
    """Parse a SKILL.md into (frontmatter_dict, body_str).

    Tiny YAML subset: handles top-level scalar keys, folded scalars (>),
    and YAML lists of strings. Avoids a PyYAML dependency since the
    frontmatter we author is simple and known.
    """
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    raw_fm, body = parts[1], parts[2].lstrip("\n")

    fm: dict[str, object] = {}
    current_key: str | None = None
    folded_lines: list[str] = []
    list_items: list[str] | None = None

    def flush_folded() -> None:
        nonlocal folded_lines, current_key
        if current_key is not None and folded_lines:
            fm[current_key] = " ".join(s.strip() for s in folded_lines).strip()
        folded_lines = []

    def flush_list() -> None:
        nonlocal list_items, current_key
        if current_key is not None and list_items is not None:
            fm[current_key] = list_items
        list_items = None

    for raw_line in raw_fm.splitlines():
        line = raw_line.rstrip()
        if not line.strip():
            continue
        # List item under current key
        m_list = re.match(r"^\s+-\s+(.+)$", raw_line)
        if m_list and list_items is not None:
            val = m_list.group(1).strip()
            if (val.startswith('"') and val.endswith('"')) or (
                val.startswith("'") and val.endswith("'")
            ):
                val = val[1:-1]
            list_items.append(val)
            continue
        # Continuation of folded scalar (indented, no colon-start)
        if raw_line.startswith(" ") and current_key and list_items is None:
            folded_lines.append(raw_line)
            continue
        # New key
        m_key = re.match(r"^([A-Za-z_][\w-]*)\s*:\s*(.*)$", line)
        if m_key:
            flush_folded()
            flush_list()
            current_key = m_key.group(1)
            value = m_key.group(2).strip()
            if value == ">" or value == "":
                # folded scalar or list incoming
                if value == ">":
                    folded_lines = []
                    list_items = None
                else:
                    list_items = []
                    folded_lines = []
            else:
                if (value.startswith('"') and value.endswith('"')) or (
                    value.startswith("'") and value.endswith("'")
                ):
                    value = value[1:-1]
                fm[current_key] = value
                current_key = None
    flush_folded()
    flush_list()
    return fm, body


def load_skills() -> dict[str, Skill]:
    """Walk the skills/ directory and parse every SKILL.md. Cached."""
    global _cache
    if _cache is not None:
        return _cache
    skills: dict[str, Skill] = {}
    if not SKILLS_DIR.exists():
        _cache = skills
        return _cache
    for skill_dir in sorted(SKILLS_DIR.iterdir()):
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.is_file():
            continue
        fm, body = _parse_skill_md(skill_md.read_text(encoding="utf-8"))
        name = str(fm.get("name") or skill_dir.name)
        description = str(fm.get("description") or "")
        raw_triggers = fm.get("triggers")
        triggers: tuple[str, ...]
        if isinstance(raw_triggers, list):
            triggers = tuple(str(t).lower() for t in raw_triggers)
        else:
            triggers = ()
        skills[name] = Skill(name=name, description=description, triggers=triggers, body=body)
    _cache = skills
    return _cache


def route_skills(message: str, history: Iterable[dict] | None = None) -> list[Skill]:
    """Pick at most 2 skills whose triggers match the user message.

    Matches are case-insensitive substring matches. Skills are scored by
    number of distinct trigger phrases that hit; ties broken by insertion
    order (i.e. directory sort order).
    """
    msg = (message or "").lower()
    if not msg.strip():
        return []
    scored: list[tuple[int, int, Skill]] = []
    for idx, skill in enumerate(load_skills().values()):
        score = sum(1 for t in skill.triggers if t and t in msg)
        if score > 0:
            scored.append((-score, idx, skill))
    scored.sort()
    return [s for _, _, s in scored[:2]]


def build_skill_block(skills: list[Skill]) -> str:
    """Concatenate the active skills' bodies into a system-prompt section."""
    if not skills:
        return ""
    parts = ["## Active skills for this turn",
             "Follow the guidance in each skill below for this reply. If multiple are listed, integrate them naturally.\n"]
    for s in skills:
        parts.append(f"### {s.name}\n\n{s.body.strip()}\n")
    return "\n".join(parts)

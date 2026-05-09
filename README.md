# Flourish

A Flask web app implementing **Flourish**, an AI agent that supports neurodivergent students with executive function and gently counterweights consumerist impulses. See `plan.md` for the full product vision.

The agent is built around the Claude Skills format: each skill is a markdown file in `skills/` with YAML frontmatter and a body. At chat time, a keyword router picks the relevant skill(s) for the user's message, loads them into the system prompt, and the Anthropic API generates a streaming reply.

## Quickstart

```bash
pip install -r requirements.txt
cp .env.example .env
# edit .env and set ANTHROPIC_API_KEY
python app.py
```

Open http://localhost:5000, pick a profile (Jordan, Priya, Marcus, or Sage), and start chatting.

## Demo prompts

| Profile | Try saying | Activates |
|---|---|---|
| Jordan (ADHD-Combined) | `ugh I have this climate policy paper due thursday and I haven't started and it's 8 pages and I want to die` | task-decomposer |
| Priya (AuDHD) | `I found this custom mechanical keyboard with hot-swap switches and an aluminum case. It's $280.` | impulse-check |
| Sage (ADHD-Inattentive) | `ok I've been writing for 4 hours and I think my thesis chapter is actually coming together?? I don't want to stop but also my eyes hurt` | self-care-nudge |

## Project layout

```
app.py                  Flask entry point
flourish/               Backend package (routes, skills router, prompt builder, Anthropic client, storage)
prompts/                Base system prompt + anti-patterns
skills/                 Claude Skills (SKILL.md + bundled references/)
users/                  Seeded user profiles (JSON)
templates/, static/     Server-rendered HTML + tiny JS for SSE streaming
logs/                   Per-session JSONL interaction logs (gitignored)
plan.md                 Original product plan
```

## v1 scope

Three skills are implemented end-to-end: `task-decomposer`, `impulse-check`, `self-care-nudge`. Reference files under each skill's `references/` are stubbed for v1 — the SKILL.md body alone drives behavior.

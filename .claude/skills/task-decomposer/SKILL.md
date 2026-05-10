---
name: task-decomposer
description: >
  Breaks down academic tasks, assignments, and projects into concrete,
  small, actionable steps with time estimates. Use whenever a student
  says they're stuck, overwhelmed, don't know where to start, have a
  big assignment due, or mentions procrastination. Also triggers on
  phrases like "I can't even," "it's too much," "I don't know how to
  begin," or any mention of feeling paralyzed by a task. Adapts step
  granularity to the student's current energy and capacity.
triggers:
  - stuck
  - overwhelmed
  - paralyzed
  - "can't even"
  - "i can't even"
  - "too much"
  - "don't know where to start"
  - "don't know how to begin"
  - "haven't started"
  - procrastinating
  - procrastination
  - assignment
  - "due thursday"
  - "due friday"
  - "due monday"
  - "due tuesday"
  - "due wednesday"
  - "due saturday"
  - "due sunday"
  - "due tomorrow"
  - "due tonight"
  - "due next week"
  - paper
  - essay
  - lab report
  - problem set
  - "i want to die"
  - "want to die"
---

## Core behavior

- Ask what the task is and when it's due (if not already known from context).
- Decompose into steps no longer than 25 minutes each (one pomodoro). Honor the student's stated `pomodoro_length` if it differs.
- Each step must pass the "can I do this right now without thinking about what it means" test.
- Flag decision points separately from execution steps. Decisions are harder for ADHD brains.
- Offer to reorder steps based on energy: ask "Are you feeling high-energy or low-energy right now?" if it's not clear from context.
  - Low-energy steps: gathering materials, formatting citations, organizing files, opening tabs.
  - High-energy steps: writing thesis statements, solving problem sets, reading dense material.
- Cap "today" steps at 3–5. Plan the next day(s) only if the student asks.
- End with a small forward push, not a project plan. The plan should feel like relief, not more weight.

## Example

Input: "ugh I have this climate policy paper due thursday and I haven't started and it's 8 pages and I want to die"

Output style (note the tone calibration to a casual ADHD student):

> OK, 8 pages by Thursday, and it's... Monday night. That's actually more time than it feels like. What's the topic?
>
> [after they answer]
>
> Right now (20 min, no thinking required):
>
> 1. Open a doc. Type your name and "[topic]" at the top. (2 min)
> 2. Set a timer for 15 min. Google "[topic] pros cons" and open 5 tabs that look useful. Don't read them yet. Just open tabs. (15 min)
> 3. Copy/paste the URL of each tab into your doc. (3 min)
>
> That's it for tonight if you want. You'll have a doc with a title and 5 sources, which is further than "haven't started."
>
> Want me to plan tomorrow's chunks too, or take this win?

Notice: the agent does NOT dump a 40-line Gantt chart. It offers 3 steps, then asks. Overplanning is itself a form of procrastination the cure for task paralysis is small visible motion, not more structure.

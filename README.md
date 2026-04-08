# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Smarter Scheduling

The scheduler goes beyond a basic task list with four algorithmic improvements:

### Sort by time
`Scheduler.sort_by_time()` orders all tasks chronologically using their `start_time` field (stored as `"HH:MM"`).
Zero-padded strings sort correctly with a plain lambda key — no date parsing needed.
Tasks without a `start_time` fall to the end via a `"99:99"` sentinel value.

### Filter by pet or status
`Scheduler.filter_tasks(completed, pet_name)` lets you slice the task list in two ways:
- `completed=False` — pending tasks only
- `completed=True` — completed tasks only
- `pet_name="Max"` — tasks for a specific pet (case-insensitive)

Both filters can be combined: `filter_tasks(completed=False, pet_name="Max")`.

### Recurring tasks
`Task.mark_completed()` now returns a **new Task instance** for the next occurrence instead of just setting a flag.
It uses Python's `timedelta` to calculate the next due date:
- `"daily"` frequency → `today + timedelta(days=1)`
- `"weekly"` frequency → `today + timedelta(weeks=1)`
- `"as-needed"` and other frequencies → returns `None` (no auto-recurrence)

### Conflict detection
`Scheduler.detect_conflicts()` checks every pair of timed tasks for overlapping windows using the formula:

```
conflict if: a_start < b_end  AND  b_start < a_end
```

It returns plain warning strings and never crashes the program.
Tasks without a `start_time` are safely skipped.

---

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

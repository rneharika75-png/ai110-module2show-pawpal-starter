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

## Testing PawPal+

### Run the tests

```bash
python -m pytest tests/test_pawpal.py -v
```

### What the tests cover

| Suite | Tests | What is verified |
|---|---|---|
| `TestTaskCompletion` | 4 | Task starts incomplete; `mark_completed()` sets flag and timestamp; repeated calls update timestamp |
| `TestTaskAdditionToPet` | 5 | Pet starts with no tasks; adding tasks increments count; duplicates are rejected; `get_info()` reflects count |
| `TestSchedulerIntegration` | 3 | `get_all_tasks()` aggregates from one pet, multiple pets; `load_all_tasks()` populates scheduler |
| `TestTaskPriorities` | 3 | Default priority is MEDIUM; `set_priority()` updates correctly; invalid input raises `ValueError` |
| `TestTaskFrequency` | 3 | Daily always due; weekly due if never completed; as-needed due until marked done |
| `TestSortByTime` | 4 | Out-of-order tasks sorted chronologically; no-`start_time` tasks go last; empty and single-task edge cases |
| `TestRecurrenceLogic` | 6 | Daily next due = today + 1 day; weekly = today + 7 days; as-needed returns `None`; original marked done; fields preserved on clone |
| `TestConflictDetection` | 6 | Overlapping windows flagged; back-to-back not flagged; same start time flagged; untimed tasks skipped; 3-way conflicts all reported |

**Total: 34 tests — 34 passing**

### Confidence Level

★★★★☆ (4/5)

The core scheduling behaviors — priority ordering, recurring tasks, conflict detection, and filtering — are all covered with both happy paths and edge cases. One star held back because the greedy `generate_schedule()` itself does not yet have dedicated integration tests, and the Streamlit UI layer is untested.

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

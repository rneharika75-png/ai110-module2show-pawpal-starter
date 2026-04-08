# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

### Core User Actions

PawPal+ should enable three fundamental user actions:

1. **Enter owner and pet information** — The user sets up their profile and pet details (name, age, etc.) so the system understands who they are and what pet they care for.

2. **Add and manage pet care tasks** — The user can create and edit tasks such as walks, feeding, medications, enrichment, and grooming. Each task includes duration and priority level to help the system schedule appropriately.

3. **Generate and view a daily schedule** — The system analyzes all tasks and constraints (time available, priority, owner preferences) to create an optimized daily plan and explains the reasoning behind its scheduling decisions.

**Initial UML Design:**

My design includes five core classes:

1. **Owner** — Stores owner name, available time per day, scheduling preferences, and constraints.
2. **Pet** — Stores pet information (name, type, age) and special needs.
3. **Task** — Represents a single pet care activity with attributes: name, duration, priority, frequency, and optional preferred time.
4. **Scheduler** — The central orchestrator that holds references to Owner, Pet, and a list of Tasks.
5. **DailySchedule** — Holds the output: scheduled tasks with assigned times, total time used, and reasoning.

The key design decision was making **Scheduler** the central orchestrator rather than embedding logic in Owner or Task. This separates concerns: data (Owner/Pet/Task) from logic (Scheduler) from presentation (DailySchedule).

**b. Design changes**

Yes, several things changed once I actually started implementing:

**1. Added Priority Enum**
- Original: priority was a plain string ("high", "medium", "low")
- Change: Created a `Priority` enum with numeric values (HIGH=3, MEDIUM=2, LOW=1)
- Why: You can't sort strings reliably. The enum made comparison and sorting clean and safe.

**2. Owner went from one pet to a list of pets**
- Original: `Owner.pet` held a single Pet reference
- Change: `Owner.pets` became a list
- Why: The demo in main.py used two pets (Max the dog, Whiskers the cat). A single-pet design would have broken that immediately.

**3. Task gained several new fields during Phase 3**
- Added `start_time` (HH:MM string), `due_date`, `completed`, and `last_completed`
- Why: These were needed for sorting by time, recurring task logic, and filtering by status. They weren't in the original UML because I hadn't thought through those features yet.

**4. Added unscheduled_tasks to DailySchedule**
- Why: It's not useful to just see what got scheduled — you also need to know what didn't fit and why.

**5. validate_feasibility() added alongside evaluate_constraints()**
- Why: A bool return tells you pass/fail. A (bool, message) tuple tells you *why* it failed, which is what the UI actually needs to display.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers three constraints in order:

1. **Time** — the owner's `available_time` is the hard ceiling. No task gets scheduled if it would push the total over that limit.
2. **Priority** — tasks are sorted HIGH → MEDIUM → LOW before the greedy fill runs. This guarantees critical care (feeding, medication) always lands before optional tasks (grooming, enrichment).
3. **Preferred time slot** — within the same priority level, tasks are ordered morning → afternoon → evening, so the schedule flows naturally through the day.

I decided time was the hardest constraint because you literally cannot do more than the hours in a day. Priority came second because a pet owner would rather skip a low-priority task than a high-priority one — that felt like the most realistic real-world behavior.

**b. Tradeoffs**

The biggest tradeoff is that the scheduler is **greedy** — it picks tasks in priority order and fills the day until time runs out. It does not try to find the globally optimal combination of tasks.

That means a single long HIGH-priority task could eat up all available time and push out three short MEDIUM tasks that would have fit together. A smarter scheduler would explore combinations, but that would be much more complex to implement and explain.

For a pet care app, greedy is a reasonable tradeoff. The schedules it produces are predictable and easy to explain to the user: "I scheduled the most important things first." That transparency matters more than mathematical optimality when a real person is trusting the app with their pet's care.

---

## 3. AI Collaboration

**a. How you used AI**

I used AI throughout all three phases but in different ways each time.

In Phase 1, I used it mostly for design brainstorming — asking things like "what methods should a Scheduler class have?" and "what's the difference between a Task and a DailySchedule?" It helped me think through the UML before writing a single line of code.

In Phase 2, I used it to implement the stub methods. The most useful prompts were specific ones like "implement is_due_today() for daily, weekly, and as-needed frequencies" rather than vague ones like "build the scheduler." Specific prompts got specific, usable code.

In Phase 3, I used it for the algorithmic pieces — sorting with a lambda key, conflict detection with interval math, and the timedelta recurrence logic. These were the kinds of problems where knowing the right Python pattern matters more than knowing the business logic.

**b. Judgment and verification**

The clearest example was the conflict detection. The AI's first suggestion was to check whether two tasks share the same `preferred_time` slot (like both being "morning"). I pushed back on that because "morning" is a label, not a time — two tasks labeled "morning" don't actually conflict if one runs at 07:00 and the other at 09:30.

I asked for a proper interval overlap check instead: `a_start < b_end AND b_start < a_end`. That formula operates on actual HH:MM start times and durations, so it catches real scheduling collisions and ignores ones that aren't real. I also added a specific test for the back-to-back edge case (tasks that touch but don't overlap) to make sure the formula didn't produce false positives.

Running the test suite after every significant change was how I verified things. If a suggestion passed all 34 tests, I kept it. If it broke something, I diagnosed why before either fixing or rejecting it.

---

## 4. Testing and Verification

**a. What you tested**

I tested five main categories:

- **Task lifecycle** — starts incomplete, mark_completed() sets the flag and timestamp, repeated calls update the timestamp
- **Pet task management** — add_task() works, duplicates are rejected, get_info() reflects the real count
- **Sorting** — tasks added out of order come back chronological, tasks with no start_time go last
- **Recurrence** — daily task returns a new instance due tomorrow, weekly due in 7 days, as-needed returns None
- **Conflict detection** — overlapping windows are flagged, back-to-back tasks are not, same start time is caught

These were the most important because they're the behaviors the UI depends on directly. If sort_by_time() returns the wrong order, the user sees a confusing task list. If conflict detection produces false positives, the user gets unnecessary warnings and loses trust in the app.

**b. Confidence**

I'd say 4 out of 5. The core scheduling behaviors are solid and well-tested with both happy paths and edge cases. The one gap is that `generate_schedule()` as a whole doesn't have its own integration test — I tested its pieces (prioritize_tasks, detect_conflicts, validate_feasibility) separately but not the full greedy fill end-to-end. That's the next thing I'd add if I had more time.

---

## 5. Reflection

**a. What went well**

The part I'm most satisfied with is the conflict detection. It went through a real design iteration — started with a naive slot-label approach, got pushed to a proper interval overlap formula, and then got a dedicated test suite that covers the tricky edge cases (back-to-back, same start, no start_time). That whole arc felt like real software engineering rather than just following instructions.

The test suite also turned out better than I expected. Having 34 tests across 8 classes gave me genuine confidence when refactoring — I could change the internals of mark_completed() and immediately know if I broke anything.

**b. What you would improve**

If I had another iteration I'd redesign how tasks are stored. Right now tasks live on the Pet object AND get loaded into the Scheduler's tasks_list, which creates two sources of truth. If you mark a task complete in the Scheduler, the Pet's copy doesn't automatically update. I'd move toward tasks living in one place (probably the Scheduler or a shared task store) with everything else holding references to them.

I'd also add a proper time-slot assignment in generate_schedule() so the output shows actual clock times ("08:00 — Morning Walk") instead of just slot labels ("morning — Morning Walk").

**c. Key takeaway**

The most important thing I learned is that AI makes you faster but not automatically smarter about design. It can generate a working implementation of almost anything you describe — but it doesn't know whether that implementation fits your system's overall structure, or whether it creates hidden problems downstream.

The moment I felt most like a "lead architect" was when I rejected the slot-label conflict detection and asked for the interval math instead. The AI gave me something that worked in a simple case, but I had to recognize that it wouldn't work in the real use case. That judgment — knowing what "correct" actually means for your specific system — doesn't come from the AI. It comes from understanding your own design well enough to evaluate what you're being handed.

That's the skill I'll carry forward: not how to prompt AI, but how to think clearly enough about a system that I can tell the difference between code that passes a test and code that actually solves the problem.

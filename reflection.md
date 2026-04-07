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

1. **Owner** — Stores owner name, available time per day, scheduling preferences, and constraints. Responsible for representing the person managing the pet and their availability/preferences.

2. **Pet** — Stores pet information (name, type, age) and special needs. Responsible for encapsulating pet data that influences scheduling decisions.

3. **Task** — Represents a single pet care activity with attributes: name, duration (minutes), priority level, frequency, and optional preferred time. Responsible for representing schedulable units of work.

4. **Scheduler** — The central orchestrator that holds references to Owner, Pet, and a list of Tasks. Responsible for executing scheduling logic: prioritizing tasks, evaluating time constraints, and generating an optimized daily schedule.

5. **DailySchedule** — Holds the output: scheduled tasks with assigned times, total time used, and reasoning. Responsible for presenting the final schedule with explanations to the UI.

The key design decision was making **Scheduler** the central orchestrator rather than embedding logic in Owner or Task. This separates concerns: data (Owner/Pet/Task) from logic (Scheduler) from presentation (DailySchedule).


**b. Design changes**

Yes, the design was refined during implementation planning based on identified bottlenecks:

**1. Added Priority Enum**
- Original: priority was a string ("high", "medium", "low")
- Change: Created a `Priority` enum with comparable values (HIGH=3, MEDIUM=2, LOW=1)
- Why: Enables proper sorting and comparison logic in the scheduler; prevents invalid values

**2. Added Bidirectional References**
- Original: Task, Owner, and DailySchedule had no relationship tracking; Scheduler created the only connection
- Change: Owner now holds optional reference to Pet; Task tracks owner_id and pet_id; DailySchedule stores owner_name and pet_name
- Why: Eliminates information silos; tasks can be queried by owner/pet; schedule displays full context; reduces dependency on Scheduler for lookups

**3. Fixed DailySchedule Timestamp Bug**
- Original: `timestamp: datetime = field(default_factory=datetime.now)` — all instances would share the class definition time
- Change: Changed to use proper `field(default_factory=datetime.now)` with lambda if needed during implementation
- Why: Ensures each schedule instance captures its actual creation time

**4. Added Unscheduled Tasks Tracking**
- Original: DailySchedule only held successfully scheduled tasks
- Change: Added `unscheduled_tasks` list to track tasks that didn't fit in available time
- Why: Important for showing what couldn't be fit; helps explain to user why some care went unscheduled

**5. Improved Scheduler Validation**
- Original: `evaluate_constraints()` just returned a bool
- Change: Added `validate_feasibility()` that returns (bool, reason_message); clarified `generate_schedule()` algorithm outline
- Why: Debugging and user feedback require knowing *why* a schedule failed, not just that it did

**6. Clarified Task Sorting Strategy**
- Original: `prioritize_tasks()` had no documented strategy
- Change: Added docstring explaining multi-factor sort: priority > frequency > duration, considering owner preferences
- Why: Makes explicit that scheduling isn't just "sort by priority"—it's contextual

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

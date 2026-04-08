"""
main.py - Demo and testing script for PawPal+ system
Tests the core functionality by creating owners, pets, tasks, and generating schedules
"""

from pawpal_system import Owner, Pet, Task, Scheduler, Priority


def main():
    """Main demo: Create owner, pets, tasks, and generate daily schedule."""

    # ── Owner & Pets ───────────────────────────────────────────────────────────
    print("=" * 60)
    print("CREATING OWNER AND PETS")
    print("=" * 60)

    owner = Owner(name="Sarah", available_time=4.0)
    print(f"Owner: {owner.name}")
    print(f"Available time: {owner.available_time} hours/day\n")

    dog = Pet(name="Max", type="Golden Retriever", age=3)
    dog.add_special_need("Requires daily exercise")
    dog.add_special_need("Sensitive stomach - special diet")

    cat = Pet(name="Whiskers", type="Siamese", age=5)
    cat.add_special_need("Needs interactive play")

    owner.add_pet(dog)
    owner.add_pet(cat)

    print(f"Pet 1: {dog.name} (Type: {dog.type}, Age: {dog.age})")
    print(f"  Special needs: {', '.join(dog.special_needs)}")
    print(f"Pet 2: {cat.name} (Type: {cat.type}, Age: {cat.age})")
    print(f"  Special needs: {', '.join(cat.special_needs)}\n")

    # ── Tasks added OUT OF ORDER (intentionally scrambled times) ──────────────
    print("=" * 60)
    print("ADDING TASKS (out of chronological order)")
    print("=" * 60)

    afternoon_walk = Task(
        name="Afternoon Walk",
        duration=30,
        priority=Priority.MEDIUM,
        frequency="daily",
        description="Second walk for bathroom break and fresh air",
        preferred_time="afternoon",
        start_time="14:00",
        pet_id="Max",
    )
    cat_play = Task(
        name="Interactive Play (Cat)",
        duration=20,
        priority=Priority.MEDIUM,
        frequency="daily",
        description="Engage Whiskers with laser pointer and toys",
        preferred_time="afternoon",
        start_time="15:30",
        pet_id="Whiskers",
    )
    feeding_dog = Task(
        name="Feeding (Dog)",
        duration=15,
        priority=Priority.HIGH,
        frequency="daily",
        description="Feed Max his special diet kibble",
        preferred_time="morning",
        start_time="07:00",
        pet_id="Max",
    )
    cat_feeding = Task(
        name="Feeding (Cat)",
        duration=10,
        priority=Priority.HIGH,
        frequency="daily",
        description="Feed Whiskers wet food",
        preferred_time="morning",
        start_time="07:15",
        pet_id="Whiskers",
    )
    morning_walk = Task(
        name="Morning Walk",
        duration=30,
        priority=Priority.HIGH,
        frequency="daily",
        description="Walk Max around the park for exercise",
        preferred_time="morning",
        start_time="08:00",
        pet_id="Max",
    )
    play_session = Task(
        name="Play Session",
        duration=20,
        priority=Priority.MEDIUM,
        frequency="daily",
        description="Interactive play with dog toys",
        preferred_time="afternoon",
        start_time="12:30",
        pet_id="Max",
    )
    grooming = Task(
        name="Brushing",
        duration=15,
        priority=Priority.LOW,
        frequency="weekly",
        description="Brush Max's coat at least twice per week",
        preferred_time="evening",
        start_time="18:00",
        pet_id="Max",
    )

    # Add to pets
    dog.add_task(afternoon_walk)   # added out of order
    dog.add_task(feeding_dog)
    dog.add_task(play_session)
    dog.add_task(morning_walk)
    dog.add_task(grooming)
    cat.add_task(cat_play)
    cat.add_task(cat_feeding)

    # ── Scheduler setup ────────────────────────────────────────────────────────
    scheduler = Scheduler(owner)
    all_tasks = scheduler.load_all_tasks()
    print(f"Loaded {len(all_tasks)} tasks (in insertion order):")
    for t in all_tasks:
        print(f"  {t.start_time or '??:??'}  {t.name:30} [{t.priority.name}]  pet={t.pet_id}")

    # ── sort_by_time() ─────────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("SORTED BY START TIME (sort_by_time)")
    print("=" * 60)
    for t in scheduler.sort_by_time():
        print(f"  {t.start_time or '??:??'}  {t.name:30} [{t.priority.name}]")

    # ── filter_tasks() — pending only ─────────────────────────────────────────
    print("\n" + "=" * 60)
    print("FILTER: pending tasks only  (completed=False)")
    print("=" * 60)
    pending = scheduler.filter_tasks(completed=False)
    print(f"  {len(pending)} pending task(s):")
    for t in pending:
        print(f"  - {t.name}")

    # ── Step 3: Recurring task demo ───────────────────────────────────────────
    print("\n" + "=" * 60)
    print("RECURRING TASKS (mark_completed -> next occurrence)")
    print("=" * 60)

    next_feeding = feeding_dog.mark_completed()
    next_cat_feeding = cat_feeding.mark_completed()

    print(f"  '{feeding_dog.name}' marked complete.")
    if next_feeding:
        print(f"  -> Next occurrence created: due {next_feeding.due_date}  (completed={next_feeding.completed})")

    print(f"  '{cat_feeding.name}' marked complete.")
    if next_cat_feeding:
        print(f"  -> Next occurrence created: due {next_cat_feeding.due_date}  (completed={next_cat_feeding.completed})")
    print()

    print("FILTER: completed tasks only  (completed=True)")
    print("=" * 60)
    done = scheduler.filter_tasks(completed=True)
    print(f"  {len(done)} completed task(s):")
    for t in done:
        print(f"  - {t.name}")

    # ── filter_tasks() — by pet name ──────────────────────────────────────────
    print("\n" + "=" * 60)
    print("FILTER: Max's tasks only  (pet_name='Max')")
    print("=" * 60)
    max_tasks = scheduler.filter_tasks(pet_name="Max")
    for t in max_tasks:
        status = "done" if t.completed else "pending"
        print(f"  {t.start_time}  {t.name:30} [{status}]")

    print("\n" + "=" * 60)
    print("FILTER: Whiskers' pending tasks  (pet_name='Whiskers', completed=False)")
    print("=" * 60)
    whiskers_pending = scheduler.filter_tasks(completed=False, pet_name="Whiskers")
    for t in whiskers_pending:
        print(f"  {t.start_time}  {t.name}")

    # ── Step 4: Conflict detection demo ──────────────────────────────────────
    print("=" * 60)
    print("CONFLICT DETECTION (overlapping start times)")
    print("=" * 60)

    # These two tasks intentionally overlap:
    #   Vet Visit   starts 09:00, lasts 60 min → occupies 09:00–10:00
    #   Bath Time   starts 09:30, lasts 45 min → occupies 09:30–10:15
    vet_visit = Task(
        name="Vet Visit",
        duration=60,
        priority=Priority.HIGH,
        frequency="as-needed",
        start_time="09:00",
        pet_id="Max",
    )
    bath_time = Task(
        name="Bath Time",
        duration=45,
        priority=Priority.MEDIUM,
        frequency="weekly",
        start_time="09:30",
        pet_id="Max",
    )
    dog.add_task(vet_visit)
    dog.add_task(bath_time)
    scheduler.load_all_tasks()   # reload so scheduler sees the new tasks

    conflicts = scheduler.detect_conflicts()
    if conflicts:
        for msg in conflicts:
            print(f"  {msg}")
    else:
        print("  No conflicts detected.")
    print()

    # ── Generate schedule ──────────────────────────────────────────────────────
    print("=" * 60)
    print("GENERATING TODAY'S SCHEDULE")
    print("=" * 60)

    feasible, reason = scheduler.validate_feasibility()
    print(f"Feasibility check ({'OK' if feasible else 'OVER BUDGET'}): {reason}\n")

    schedule = scheduler.generate_schedule()
    print(schedule.display_plan())

    print("\n" + "=" * 60)
    print("SCHEDULE SUMMARY")
    print("=" * 60)
    print(f"Total scheduled time : {schedule.total_time_used:.2f} hrs")
    print(f"Available time       : {owner.available_time:.1f} hrs")
    print(f"Time remaining       : {owner.available_time - schedule.total_time_used:.2f} hrs")
    print(f"Scheduled tasks      : {len(schedule.scheduled_tasks)}")
    print(f"Unscheduled tasks    : {len(schedule.unscheduled_tasks)}")


if __name__ == "__main__":
    main()

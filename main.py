"""
main.py - Demo and testing script for PawPal+ system
Tests the core functionality by creating owners, pets, tasks, and generating schedules
"""

from pawpal_system import Owner, Pet, Task, Scheduler, Priority


def main():
    """Main demo: Create owner, pets, tasks, and generate daily schedule."""
    
    # Create an Owner
    print("=" * 60)
    print("CREATING OWNER AND PETS")
    print("=" * 60)
    
    owner = Owner(name="Sarah", available_time=4.0)  # 4 hours available per day
    print(f"Owner: {owner.name}")
    print(f"Available time: {owner.available_time} hours/day\n")
    
    # Create two Pets
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
    
    # Create Tasks for the dog
    print("=" * 60)
    print("ADDING TASKS")
    print("=" * 60)
    
    # High priority tasks
    morning_walk = Task(
        name="Morning Walk",
        duration=30,
        priority=Priority.HIGH,
        frequency="daily",
        description="Walk Max around the park for exercise",
        preferred_time="morning"
    )
    feeding = Task(
        name="Feeding (Dog)",
        duration=15,
        priority=Priority.HIGH,
        frequency="daily",
        description="Feed Max his special diet kibble"
    )
    
    # Medium priority tasks
    play_session = Task(
        name="Play Session",
        duration=20,
        priority=Priority.MEDIUM,
        frequency="daily",
        description="Interactive play with dog toys"
    )
    
    afternoon_walk = Task(
        name="Afternoon Walk",
        duration=30,
        priority=Priority.MEDIUM,
        frequency="daily",
        description="Second walk for bathroom break and fresh air"
    )
    
    # Low priority task
    grooming = Task(
        name="Brushing",
        duration=15,
        priority=Priority.LOW,
        frequency="weekly",
        description="Brush Max's coat at least twice per week"
    )
    
    # Tasks for the cat
    cat_feeding = Task(
        name="Feeding (Cat)",
        duration=10,
        priority=Priority.HIGH,
        frequency="daily",
        description="Feed Whiskers wet food"
    )
    
    cat_play = Task(
        name="Interactive Play (Cat)",
        duration=20,
        priority=Priority.MEDIUM,
        frequency="daily",
        description="Engage Whiskers with laser pointer and toys"
    )
    
    # Add tasks to pets
    dog.add_task(morning_walk)
    dog.add_task(feeding)
    dog.add_task(play_session)
    dog.add_task(afternoon_walk)
    dog.add_task(grooming)
    
    cat.add_task(cat_feeding)
    cat.add_task(cat_play)
    
    tasks = [morning_walk, feeding, play_session, afternoon_walk, grooming, cat_feeding, cat_play]
    
    print(f"Added {len(tasks)} tasks total:")
    for task in tasks:
        print(f"  - {task.name}: {task.duration}min [{task.priority.name}] ({task.frequency})")
    print()
    
    # Create Scheduler and generate schedule
    print("=" * 60)
    print("GENERATING TODAY'S SCHEDULE")
    print("=" * 60)
    print()
    
    scheduler = Scheduler(owner)
    
    # Load all tasks from owner's pets
    all_tasks = scheduler.load_all_tasks()
    print(f"Scheduler loaded {len(all_tasks)} tasks from owner's pets")
    
    # Check feasibility
    is_feasible, reason = scheduler.validate_feasibility()
    print(f"Feasibility check: {reason}\n")
    
    # Generate the schedule
    schedule = scheduler.generate_schedule()
    
    # Display the schedule
    print(schedule.display_plan())
    print()
    
    # Additional info
    print("=" * 60)
    print("SCHEDULE SUMMARY")
    print("=" * 60)
    print(f"Total scheduled time: {schedule.total_time_used:.1f} hours")
    print(f"Available time: {owner.available_time:.1f} hours")
    print(f"Time remaining: {owner.available_time - schedule.total_time_used:.1f} hours")
    print(f"Scheduled tasks: {len(schedule.scheduled_tasks)}")
    print(f"Unscheduled tasks: {len(schedule.unscheduled_tasks)}")
    print()


if __name__ == "__main__":
    main()

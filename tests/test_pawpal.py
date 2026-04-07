"""
test_pawpal.py - Unit tests for PawPal+ system
Tests core functionality of Task, Pet, Owner, and Scheduler classes
"""

import pytest
from datetime import datetime
from pawpal_system import Owner, Pet, Task, Scheduler, Priority


class TestTaskCompletion:
    """Test suite for Task completion functionality."""
    
    def test_task_initially_not_completed(self):
        """Verify that a new task starts with completed=False."""
        task = Task(
            name="Morning Walk",
            duration=30,
            priority=Priority.HIGH,
            frequency="daily"
        )
        assert task.completed is False
    
    def test_mark_completed_changes_status(self):
        """Verify that calling mark_completed() changes the task's completed status to True."""
        task = Task(
            name="Feeding",
            duration=15,
            priority=Priority.HIGH,
            frequency="daily"
        )
        
        # Initially not completed
        assert task.completed is False
        assert task.last_completed is None
        
        # Mark as completed
        task.mark_completed()
        
        # Verify status changed
        assert task.completed is True
        assert task.last_completed is not None
    
    def test_mark_completed_sets_timestamp(self):
        """Verify that mark_completed() records the completion time."""
        task = Task(
            name="Medication",
            duration=5,
            priority=Priority.HIGH
        )
        
        before_completion = datetime.now()
        task.mark_completed()
        after_completion = datetime.now()
        
        # last_completed should be set and between before/after times
        assert task.last_completed is not None
        assert before_completion <= task.last_completed <= after_completion
    
    def test_mark_completed_multiple_times(self):
        """Verify that mark_completed() can be called multiple times (updates timestamp)."""
        task = Task(
            name="Play Session",
            duration=20,
            priority=Priority.MEDIUM
        )
        
        # First completion
        task.mark_completed()
        first_timestamp = task.last_completed
        
        # Wait a tiny bit and complete again
        import time
        time.sleep(0.01)
        
        task.mark_completed()
        second_timestamp = task.last_completed
        
        # Second timestamp should be later
        assert second_timestamp > first_timestamp
        assert task.completed is True


class TestTaskAdditionToPet:
    """Test suite for adding tasks to pets."""
    
    def test_pet_starts_with_no_tasks(self):
        """Verify that a new pet has an empty task list."""
        pet = Pet(name="Max", type="Dog", age=3)
        assert len(pet.tasks) == 0
        assert pet.tasks == []
    
    def test_add_task_to_pet_increases_count(self):
        """Verify that adding a task to a Pet increases that pet's task count."""
        pet = Pet(name="Whiskers", type="Cat", age=5)
        
        # Initially no tasks
        initial_count = len(pet.tasks)
        assert initial_count == 0
        
        # Add a task
        task1 = Task(
            name="Feeding",
            duration=10,
            priority=Priority.HIGH
        )
        pet.add_task(task1)
        
        # Count should increase by 1
        assert len(pet.tasks) == 1
        assert pet.tasks[0] == task1
    
    def test_add_multiple_tasks_to_pet(self):
        """Verify that multiple tasks can be added and count increases correctly."""
        pet = Pet(name="Buddy", type="Dog", age=2)
        
        task1 = Task(name="Morning Walk", duration=30, priority=Priority.HIGH)
        task2 = Task(name="Feeding", duration=15, priority=Priority.HIGH)
        task3 = Task(name="Play", duration=20, priority=Priority.MEDIUM)
        
        pet.add_task(task1)
        assert len(pet.tasks) == 1
        
        pet.add_task(task2)
        assert len(pet.tasks) == 2
        
        pet.add_task(task3)
        assert len(pet.tasks) == 3
        
        # Verify all tasks are in the list
        assert task1 in pet.tasks
        assert task2 in pet.tasks
        assert task3 in pet.tasks
    
    def test_duplicate_task_not_added_twice(self):
        """Verify that adding the same task twice doesn't create duplicates."""
        pet = Pet(name="Bella", type="Cat", age=1)
        
        task = Task(name="Grooming", duration=15, priority=Priority.LOW)
        
        # Add the same task twice
        pet.add_task(task)
        pet.add_task(task)
        
        # Count should still be 1 (not 2)
        assert len(pet.tasks) == 1
    
    def test_pet_get_info_reflects_task_count(self):
        """Verify that get_info() returns accurate task count."""
        pet = Pet(name="Max", type="Dog", age=3)
        
        # No tasks
        info = pet.get_info()
        assert info["task_count"] == 0
        
        # Add tasks
        pet.add_task(Task(name="Walk", duration=30, priority=Priority.HIGH))
        pet.add_task(Task(name="Feed", duration=15, priority=Priority.HIGH))
        
        info = pet.get_info()
        assert info["task_count"] == 2
        assert info["name"] == "Max"
        assert info["type"] == "Dog"
        assert info["age"] == 3


class TestSchedulerIntegration:
    """Test suite for Scheduler integration with Owner and Pets."""
    
    def test_owner_get_all_tasks_from_one_pet(self):
        """Verify that Owner.get_all_tasks() retrieves all tasks from owned pets."""
        owner = Owner(name="Sarah", available_time=4.0)
        pet = Pet(name="Max", type="Dog", age=3)
        
        task1 = Task(name="Walk", duration=30, priority=Priority.HIGH)
        task2 = Task(name="Feed", duration=15, priority=Priority.HIGH)
        task3 = Task(name="Play", duration=20, priority=Priority.MEDIUM)
        
        pet.add_task(task1)
        pet.add_task(task2)
        pet.add_task(task3)
        owner.add_pet(pet)
        
        all_tasks = owner.get_all_tasks()
        
        assert len(all_tasks) == 3
        assert task1 in all_tasks
        assert task2 in all_tasks
        assert task3 in all_tasks
    
    def test_owner_get_all_tasks_from_multiple_pets(self):
        """Verify that Owner.get_all_tasks() retrieves tasks from all pets."""
        owner = Owner(name="Sarah", available_time=4.0)
        
        dog = Pet(name="Max", type="Dog", age=3)
        cat = Pet(name="Whiskers", type="Cat", age=5)
        
        # Dog tasks
        dog_task1 = Task(name="Dog Walk", duration=30, priority=Priority.HIGH)
        dog_task2 = Task(name="Dog Feed", duration=15, priority=Priority.HIGH)
        dog.add_task(dog_task1)
        dog.add_task(dog_task2)
        
        # Cat tasks
        cat_task1 = Task(name="Cat Feed", duration=10, priority=Priority.HIGH)
        cat_task2 = Task(name="Cat Play", duration=20, priority=Priority.MEDIUM)
        cat.add_task(cat_task1)
        cat.add_task(cat_task2)
        
        owner.add_pet(dog)
        owner.add_pet(cat)
        
        all_tasks = owner.get_all_tasks()
        
        assert len(all_tasks) == 4
        assert dog_task1 in all_tasks
        assert dog_task2 in all_tasks
        assert cat_task1 in all_tasks
        assert cat_task2 in all_tasks
    
    def test_scheduler_loads_all_tasks(self):
        """Verify that Scheduler.load_all_tasks() populates the task list."""
        owner = Owner(name="Sarah", available_time=4.0)
        pet = Pet(name="Max", type="Dog", age=3)
        
        task1 = Task(name="Walk", duration=30, priority=Priority.HIGH)
        task2 = Task(name="Feed", duration=15, priority=Priority.HIGH)
        
        pet.add_task(task1)
        pet.add_task(task2)
        owner.add_pet(pet)
        
        scheduler = Scheduler(owner)
        assert len(scheduler.tasks_list) == 0  # Initially empty
        
        loaded_tasks = scheduler.load_all_tasks()
        
        assert len(scheduler.tasks_list) == 2
        assert len(loaded_tasks) == 2
        assert task1 in scheduler.tasks_list
        assert task2 in scheduler.tasks_list


class TestTaskPriorities:
    """Test suite for task priority handling."""
    
    def test_task_default_priority_is_medium(self):
        """Verify that task default priority is MEDIUM."""
        task = Task(name="Task", duration=10)
        assert task.priority == Priority.MEDIUM
        assert task.get_priority() == Priority.MEDIUM
    
    def test_set_priority(self):
        """Verify that set_priority() updates the priority."""
        task = Task(name="Task", duration=10, priority=Priority.LOW)
        assert task.priority == Priority.LOW
        
        task.set_priority(Priority.HIGH)
        assert task.priority == Priority.HIGH
        assert task.get_priority() == Priority.HIGH
    
    def test_set_priority_with_invalid_type_raises_error(self):
        """Verify that set_priority() rejects invalid priority types."""
        task = Task(name="Task", duration=10)
        
        with pytest.raises(ValueError):
            task.set_priority("invalid")


class TestTaskFrequency:
    """Test suite for task frequency and due date logic."""
    
    def test_daily_task_is_always_due(self):
        """Verify that daily tasks are always due today."""
        task = Task(name="Feed", duration=15, frequency="daily")
        assert task.is_due_today() is True
    
    def test_weekly_task_is_due_if_never_completed(self):
        """Verify that weekly tasks are due if last_completed is None."""
        task = Task(name="Grooming", duration=30, frequency="weekly")
        assert task.is_due_today() is True
    
    def test_as_needed_task_is_due_if_not_completed(self):
        """Verify that as-needed tasks are due if not completed."""
        task = Task(name="Bath", duration=45, frequency="as-needed")
        assert task.is_due_today() is True
        
        task.mark_completed()
        assert task.is_due_today() is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


"""
PawPal+ System Classes
Skeleton implementation with attributes and method stubs
Uses dataclasses for clean, declarative data structures
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Tuple
from enum import Enum


class Priority(Enum):
    """Task priority levels."""
    HIGH = 3
    MEDIUM = 2
    LOW = 1


@dataclass
class Owner:
    """Represents a pet owner with preferences and constraints."""
    name: str
    available_time: float  # hours per day
    pets: List['Pet'] = field(default_factory=list)  # can manage multiple pets
    preferences: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    
    def set_available_time(self, hours: float) -> None:
        """Set the owner's available time for pet care tasks."""
        if hours < 0:
            raise ValueError("Available time cannot be negative")
        self.available_time = hours
    
    def add_preference(self, preference: str) -> None:
        """Add a scheduling preference."""
        if preference not in self.preferences:
            self.preferences.append(preference)
    
    def add_constraint(self, constraint: str) -> None:
        """Add a scheduling constraint."""
        if constraint not in self.constraints:
            self.constraints.append(constraint)
    
    def get_constraints(self) -> List[str]:
        """Retrieve all owner constraints."""
        return self.constraints.copy()
    
    def add_pet(self, pet: 'Pet') -> None:
        """Add a pet to this owner's care."""
        if pet not in self.pets:
            self.pets.append(pet)
    
    def get_all_tasks(self) -> List['Task']:
        """Retrieve all tasks across all pets."""
        all_tasks = []
        for pet in self.pets:
            all_tasks.extend(pet.tasks)
        return all_tasks


@dataclass
class Pet:
    """Represents a pet owned by an owner."""
    name: str
    type: str  # dog, cat, etc.
    age: int
    special_needs: List[str] = field(default_factory=list)
    tasks: List['Task'] = field(default_factory=list)  # tasks this pet requires
    
    def get_info(self) -> dict:
        """Return pet information as a dictionary."""
        return {
            "name": self.name,
            "type": self.type,
            "age": self.age,
            "special_needs": self.special_needs.copy(),
            "task_count": len(self.tasks)
        }
    
    def add_special_need(self, need: str) -> None:
        """Add a special need or constraint for the pet."""
        if need not in self.special_needs:
            self.special_needs.append(need)
    
    def add_task(self, task: 'Task') -> None:
        """Add a task to this pet's care routine."""
        if task not in self.tasks:
            self.tasks.append(task)


@dataclass
class Task:
    """Represents a pet care task (walk, feeding, medication, etc.)."""
    name: str
    duration: int  # minutes
    priority: Priority = Priority.MEDIUM
    frequency: str = "daily"
    description: str = ""
    preferred_time: Optional[str] = None  # optional: "morning", "afternoon", etc.
    owner_id: Optional[str] = None  # reference to which owner created this task
    pet_id: Optional[str] = None  # reference to which pet needs this task
    completed: bool = False  # completion status for tracking
    last_completed: Optional[datetime] = None  # when was this task last completed
    
    def get_duration(self) -> int:
        """Return task duration in minutes."""
        return self.duration
    
    def get_priority(self) -> Priority:
        """Return task priority level."""
        return self.priority
    
    def set_priority(self, level: Priority) -> None:
        """Update task priority."""
        if not isinstance(level, Priority):
            raise ValueError(f"Priority must be a Priority enum value, got {type(level)}")
        self.priority = level
    
    def is_due_today(self) -> bool:
        """Check if task is due today based on frequency."""
        # Basic implementation: daily tasks are always due
        # Frequency check would be more complex in real implementation
        if self.frequency.lower() == "daily":
            return True
        elif self.frequency.lower() == "weekly":
            # In real implementation, check last_completed date
            return self.last_completed is None
        elif self.frequency.lower() == "as-needed":
            return not self.completed
        return False
    
    def mark_completed(self) -> None:
        """Mark task as completed."""
        self.completed = True
        self.last_completed = datetime.now()


@dataclass
class DailySchedule:
    """Represents an optimized daily schedule for pet care tasks."""
    owner_name: str
    pet_name: str
    scheduled_tasks: List[Tuple[Task, str]] = field(default_factory=list)  # List of (task, time) tuples
    total_time_used: float = 0.0  # hours
    reasoning: str = ""  # explanation of scheduling decisions
    timestamp: datetime = field(default_factory=datetime.now)
    unscheduled_tasks: List[Task] = field(default_factory=list)  # tasks that didn't fit
    
    def get_tasks_by_time(self) -> List[Tuple[Task, str]]:
        """Return tasks ordered by scheduled time."""
        # Tasks are already ordered by time in scheduled_tasks
        return self.scheduled_tasks.copy()
    
    def get_explanation(self) -> str:
        """Return explanation of why tasks are scheduled this way."""
        return self.reasoning
    
    def display_plan(self) -> str:
        """Format the plan for UI display."""
        output = []
        output.append(f"=== Daily Schedule for {self.owner_name}'s {self.pet_name} ===")
        output.append(f"Generated: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        output.append(f"Total Time: {self.total_time_used:.1f} hours")
        output.append("")
        
        if self.scheduled_tasks:
            output.append("SCHEDULED TASKS:")
            for task, time_str in self.scheduled_tasks:
                output.append(f"  {time_str} - {task.name} ({task.duration}min) [Priority: {task.priority.name}]")
        
        if self.unscheduled_tasks:
            output.append("")
            output.append(f"COULD NOT FIT ({len(self.unscheduled_tasks)} tasks):")
            for task in self.unscheduled_tasks:
                output.append(f"  - {task.name} ({task.duration}min) [Priority: {task.priority.name}]")
        
        output.append("")
        output.append("REASONING:")
        output.append(f"  {self.reasoning}")
        
        return "\n".join(output)


class Scheduler:
    """Orchestrates scheduling of pet care tasks based on owner and pet data."""
    
    def __init__(self, owner: Owner):
        self.owner = owner
        self.tasks_list = []
        self.daily_plan = None
    
    def add_task(self, task: Task) -> None:
        """Add a task to the scheduler."""
        if task not in self.tasks_list:
            self.tasks_list.append(task)
    
    def load_all_tasks(self) -> List[Task]:
        """Load all tasks from owner's pets into the scheduler."""
        all_tasks = self.owner.get_all_tasks()
        self.tasks_list = all_tasks.copy()
        return self.tasks_list
    
    def generate_schedule(self) -> DailySchedule:
        """
        Generate an optimized daily schedule based on constraints and priorities.
        
        Algorithm outline:
        1. Load all tasks from owner's pets
        2. Validate all tasks fit within available time
        3. Sort tasks by priority (high > medium > low)
        4. Consider frequency (daily > weekly > as-needed)
        5. Place tasks respecting preferred_time windows
        6. Create DailySchedule with reasoning
        """
        # Load current tasks
        self.load_all_tasks()
        
        # Check feasibility
        is_feasible, reason = self.validate_feasibility()
        if not is_feasible:
            # Still create a schedule, but mark some tasks as unscheduled
            pass
        
        # Prioritize tasks
        prioritized = self.prioritize_tasks()
        
        # Assign times and create schedule
        schedule = self._create_schedule_from_tasks(prioritized)
        self.daily_plan = schedule
        return schedule
    
    def evaluate_constraints(self) -> bool:
        """Check if all tasks fit within owner's available time."""
        total_minutes = sum(task.duration for task in self.tasks_list)
        total_hours = total_minutes / 60.0
        return total_hours <= self.owner.available_time
    
    def prioritize_tasks(self) -> List[Task]:
        """
        Sort tasks by priority, frequency, and duration. 
        Consider owner preferences.
        
        Sort order: 
        1. Priority (HIGH > MEDIUM > LOW)
        2. Frequency (daily > weekly > as-needed)
        3. Duration (shorter first for efficiency)
        """
        frequency_rank = {"daily": 3, "weekly": 2, "as-needed": 1}
        
        def sort_key(task: Task):
            freq_value = frequency_rank.get(task.frequency.lower(), 0)
            return (-task.priority.value, -freq_value, task.duration)
        
        return sorted(self.tasks_list, key=sort_key)
    
    def get_plan(self) -> DailySchedule:
        """Return the generated daily schedule."""
        return self.daily_plan
    
    def validate_feasibility(self) -> Tuple[bool, str]:
        """Check if schedule is feasible. Return (is_feasible, reason_if_not)."""
        total_minutes = sum(task.duration for task in self.tasks_list)
        total_hours = total_minutes / 60.0
        
        if total_hours > self.owner.available_time:
            deficit = total_hours - self.owner.available_time
            return (False, f"Tasks total {total_hours:.1f} hours but only {self.owner.available_time} hours available. "
                          f"Need to remove {deficit:.1f} hours of tasks.")
        
        return (True, "All tasks fit within available time.")
    
    def _create_schedule_from_tasks(self, prioritized_tasks: List[Task]) -> DailySchedule:
        """
        Internal method to create a DailySchedule from prioritized tasks.
        Assigns start times and builds the schedule object.
        """
        schedule = DailySchedule(
            owner_name=self.owner.name,
            pet_name=self.owner.pets[0].name if self.owner.pets else "Unknown"
        )
        
        current_time_minutes = 0  # Start at 00:00
        unscheduled = []
        scheduled = []
        
        for task in prioritized_tasks:
            # Check if task fits in remaining time
            if current_time_minutes + task.duration <= self.owner.available_time * 60:
                start_hour = current_time_minutes // 60
                start_min = current_time_minutes % 60
                time_str = f"{start_hour:02d}:{start_min:02d}"
                scheduled.append((task, time_str))
                current_time_minutes += task.duration
            else:
                unscheduled.append(task)
        
        schedule.scheduled_tasks = scheduled
        schedule.unscheduled_tasks = unscheduled
        schedule.total_time_used = current_time_minutes / 60.0
        
        # Generate reasoning
        schedule.reasoning = self._generate_reasoning(scheduled, unscheduled)
        
        return schedule
    
    def _generate_reasoning(self, scheduled: List[Tuple[Task, str]], 
                           unscheduled: List[Task]) -> str:
        """Generate explanation for why tasks were scheduled this way."""
        reasons = [f"Scheduled {len(scheduled)} of {len(scheduled) + len(unscheduled)} tasks."]
        
        if scheduled:
            reasons.append(f"Tasks sorted by priority (HIGH > MEDIUM > LOW) and frequency (daily > weekly).")
        
        if unscheduled:
            reasons.append(f"Could not fit {len(unscheduled)} tasks: {', '.join(t.name for t in unscheduled)}. "
                          f"Consider reducing task duration, duration, or requesting more available time.")
        
        return " ".join(reasons)

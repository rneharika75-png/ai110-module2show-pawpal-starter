"""
PawPal+ System Classes
"""

import dataclasses
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import List, Optional, Tuple
from enum import Enum


class Priority(Enum):
    """Defines task priority levels."""
    HIGH = 3
    MEDIUM = 2
    LOW = 1


@dataclass
class Owner:
    """Represents a pet owner."""
    name: str
    available_time: float
    pets: List['Pet'] = field(default_factory=list)
    preferences: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)

    def set_available_time(self, hours: float) -> None:
        """Set available time."""
        self.available_time = hours

    def add_preference(self, preference: str) -> None:
        """Add preference."""
        self.preferences.append(preference)

    def get_constraints(self) -> List[str]:
        """Get constraints."""
        return self.constraints

    def add_pet(self, pet: 'Pet') -> None:
        """Add a pet, ignoring duplicates."""
        if pet not in self.pets:
            self.pets.append(pet)

    def get_all_tasks(self) -> List['Task']:
        """Return every task from every owned pet."""
        all_tasks = []
        for pet in self.pets:
            all_tasks.extend(pet.tasks)
        return all_tasks


@dataclass
class Pet:
    """Represents a pet."""
    name: str
    type: str
    age: int
    special_needs: List[str] = field(default_factory=list)
    tasks: List['Task'] = field(default_factory=list)

    def get_info(self) -> dict:
        """Get pet info."""
        return {
            "name": self.name,
            "type": self.type,
            "age": self.age,
            "special_needs": self.special_needs,
            "task_count": len(self.tasks),
        }

    def add_special_need(self, need: str) -> None:
        """Add special need."""
        self.special_needs.append(need)

    def add_task(self, task: 'Task') -> None:
        """Add task, ignoring duplicates."""
        if task not in self.tasks:
            self.tasks.append(task)


@dataclass
class Task:
    """Represents a pet care task."""
    name: str
    duration: int
    priority: Priority = Priority.MEDIUM
    frequency: str = "daily"
    description: str = ""
    preferred_time: Optional[str] = None
    owner_id: Optional[str] = None
    pet_id: Optional[str] = None
    start_time: Optional[str] = None   # HH:MM format, e.g. "08:30"
    due_date: Optional[date] = None    # date this instance is due
    completed: bool = False
    last_completed: Optional[datetime] = None

    def get_duration(self) -> int:
        """Return the task's duration in minutes.

        Returns:
            int: Number of minutes this task takes to complete.
        """
        return self.duration

    def get_priority(self) -> Priority:
        """Return the current priority level of this task.

        Returns:
            Priority: One of Priority.HIGH, Priority.MEDIUM, or Priority.LOW.
        """
        return self.priority

    def set_priority(self, level: Priority) -> None:
        """Update the task's priority level.

        Args:
            level (Priority): The new priority. Must be a Priority enum value.

        Raises:
            ValueError: If level is not a Priority enum instance.
        """
        if not isinstance(level, Priority):
            raise ValueError(f"Expected a Priority enum value, got {type(level)}")
        self.priority = level

    def mark_completed(self) -> Optional['Task']:
        """Mark task done and return a fresh instance for the next occurrence.

        Uses timedelta to calculate the next due date:
          - daily  → today + timedelta(days=1)
          - weekly → today + timedelta(weeks=1)
        Returns None for one-off / as-needed tasks.
        """
        self.completed = True
        self.last_completed = datetime.now()

        if self.frequency == "daily":
            next_due = date.today() + timedelta(days=1)
        elif self.frequency == "weekly":
            next_due = date.today() + timedelta(weeks=1)
        else:
            return None

        return dataclasses.replace(
            self,
            completed=False,
            last_completed=None,
            due_date=next_due,
        )

    def is_due_today(self) -> bool:
        """Determine whether this task should appear in today's schedule.

        Rules by frequency:
            - ``daily``     : always due.
            - ``weekly``    : due if never completed, or if 7+ days have passed
                              since ``last_completed``.
            - ``as-needed`` : due until ``mark_completed()`` is called.
            - anything else : treated as always due.

        Returns:
            bool: True if the task should be included in today's schedule.
        """
        if self.frequency == "daily":
            return True
        if self.frequency == "weekly":
            if self.last_completed is None:
                return True
            return (datetime.now() - self.last_completed).days >= 7
        if self.frequency == "as-needed":
            return not self.completed
        return True  # unknown frequency → always include


@dataclass
class DailySchedule:
    """Represents a daily schedule."""
    owner_name: str
    pet_name: str
    scheduled_tasks: List[Tuple['Task', str]] = field(default_factory=list)
    total_time_used: float = 0.0
    reasoning: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    unscheduled_tasks: List['Task'] = field(default_factory=list)

    def get_tasks_by_time(self) -> List[Tuple['Task', str]]:
        """Return scheduled tasks sorted by time slot."""
        slot_order = {"morning": 0, "afternoon": 1, "evening": 2, "anytime": 3}
        return sorted(self.scheduled_tasks, key=lambda x: slot_order.get(x[1], 3))

    def get_explanation(self) -> str:
        """Return the scheduling reasoning."""
        return self.reasoning

    def display_plan(self) -> str:
        """Return the schedule as a formatted string."""
        lines = [
            f"Daily Schedule for {self.owner_name}",
            f"Generated: {self.timestamp.strftime('%Y-%m-%d %H:%M')}",
            "-" * 45,
        ]
        if not self.scheduled_tasks:
            lines.append("  No tasks scheduled.")
        else:
            for task, slot in self.get_tasks_by_time():
                lines.append(
                    f"  [{slot.upper():10}] {task.name}"
                    f" ({task.duration} min) [{task.priority.name}]"
                )
        if self.unscheduled_tasks:
            lines.append("\n  Skipped (time ran out):")
            for task in self.unscheduled_tasks:
                lines.append(f"    - {task.name} ({task.duration} min)")
        lines.append("-" * 45)
        lines.append(f"Total time used: {self.total_time_used:.2f} hrs")
        if self.reasoning:
            lines.append(f"Notes: {self.reasoning}")
        return "\n".join(lines)


class Scheduler:
    """Handles scheduling logic."""

    _TIME_ORDER = {"morning": 0, "afternoon": 1, "evening": 2, None: 3}

    def __init__(self, owner: Owner, pet: Optional[Pet] = None):
        """Initialize scheduler with an owner and optional single pet."""
        self.owner = owner
        self.pet = pet
        self.tasks_list: List[Task] = []
        self.daily_plan: Optional[DailySchedule] = None

    def add_task(self, task: Task) -> None:
        """Add a task, ignoring duplicates."""
        if task not in self.tasks_list:
            self.tasks_list.append(task)

    def load_all_tasks(self) -> List[Task]:
        """Load every task from all pets owned by the owner."""
        self.tasks_list = self.owner.get_all_tasks()
        return self.tasks_list

    def evaluate_constraints(self) -> bool:
        """Return True if due tasks fit within the owner's available time."""
        total_minutes = sum(t.duration for t in self.tasks_list if t.is_due_today())
        return total_minutes <= self.owner.available_time * 60

    def validate_feasibility(self) -> Tuple[bool, str]:
        """Return (feasible, explanation) for the current task list."""
        due_tasks = [t for t in self.tasks_list if t.is_due_today()]
        total_min = sum(t.duration for t in due_tasks)
        available_min = self.owner.available_time * 60
        if total_min <= available_min:
            return True, (
                f"Feasible: {total_min} min needed, {available_min:.0f} min available."
            )
        over = total_min - available_min
        return False, (
            f"Over budget by {over} min "
            f"({total_min} min needed, {available_min:.0f} min available)."
        )

    @staticmethod
    def _to_minutes(hhmm: str) -> int:
        """Convert 'HH:MM' string to minutes since midnight."""
        h, m = hhmm.split(":")
        return int(h) * 60 + int(m)

    def detect_conflicts(self) -> List[str]:
        """Return warning messages for tasks whose time windows overlap.

        Strategy: for every pair of tasks that both have a start_time, check
        whether their [start, start+duration) intervals intersect.  This is a
        lightweight O(n²) scan that warns instead of crashing.
        Tasks without a start_time are skipped (no concrete time to conflict on).
        """
        warnings: List[str] = []
        timed = [t for t in self.tasks_list if t.start_time]

        for i, a in enumerate(timed):
            for b in timed[i + 1:]:
                a_start = self._to_minutes(a.start_time)
                a_end   = a_start + a.duration
                b_start = self._to_minutes(b.start_time)
                b_end   = b_start + b.duration
                if a_start < b_end and b_start < a_end:
                    warnings.append(
                        f"WARNING: '{a.name}' ({a.start_time}, {a.duration} min) "
                        f"overlaps with '{b.name}' ({b.start_time}, {b.duration} min)"
                    )

        return warnings

    def prioritize_tasks(self) -> List[Task]:
        """Return due tasks sorted for greedy scheduling.

        Primary sort key  : priority value descending (HIGH=3 first).
        Secondary sort key: preferred time slot (morning < afternoon < evening
                            < no preference), so same-priority tasks are ordered
                            chronologically through the day.

        Returns:
            List[Task]: Due tasks in the order they should be attempted.
        """
        due = [t for t in self.tasks_list if t.is_due_today()]
        return sorted(
            due,
            key=lambda t: (-t.priority.value, self._TIME_ORDER.get(t.preferred_time, 3)),
        )

    def sort_by_time(self) -> List[Task]:
        """Return all tasks sorted chronologically by their ``start_time``.

        Uses a lambda key on the ``start_time`` string.  Zero-padded "HH:MM"
        strings sort correctly with plain string comparison because
        lexicographic order matches chronological order (e.g. "08:00" < "14:00").
        Tasks that have no ``start_time`` are placed at the end via the "99:99"
        sentinel.

        Returns:
            List[Task]: Every task in ``tasks_list``, earliest first.
        """
        return sorted(
            self.tasks_list,
            key=lambda t: t.start_time if t.start_time is not None else "99:99",
        )

    def filter_tasks(
        self,
        completed: Optional[bool] = None,
        pet_name: Optional[str] = None,
    ) -> List[Task]:
        """Filter ``tasks_list`` by completion status and/or pet name.

        Both filters are independent and can be combined.  Omitting a filter
        (leaving it as ``None``) means that criterion is not applied.

        Args:
            completed (bool | None): ``True`` returns only completed tasks,
                ``False`` returns only pending tasks, ``None`` skips this filter.
            pet_name (str | None): Case-insensitive match against each task's
                ``pet_id``.  ``None`` skips this filter.

        Returns:
            List[Task]: Tasks from ``tasks_list`` that satisfy all supplied filters.

        Examples:
            >>> scheduler.filter_tasks(completed=False)            # all pending
            >>> scheduler.filter_tasks(pet_name="Max")             # all of Max's
            >>> scheduler.filter_tasks(completed=False, pet_name="Max")  # Max's pending
        """
        result = self.tasks_list
        if completed is not None:
            result = [t for t in result if t.completed == completed]
        if pet_name is not None:
            result = [t for t in result if (t.pet_id or "").lower() == pet_name.lower()]
        return result

    def generate_schedule(self) -> DailySchedule:
        """Greedily build a daily schedule within the owner's available time."""
        sorted_tasks = self.prioritize_tasks()
        conflicts = self.detect_conflicts()

        # Resolve the pet name to display
        if self.pet:
            pet_name = self.pet.name
        elif self.owner.pets:
            pet_name = ", ".join(p.name for p in self.owner.pets)
        else:
            pet_name = "N/A"

        scheduled: List[Tuple[Task, str]] = []
        unscheduled: List[Task] = []
        time_used = 0.0

        for task in sorted_tasks:
            task_hours = task.duration / 60
            if time_used + task_hours <= self.owner.available_time:
                slot = task.preferred_time or "anytime"
                scheduled.append((task, slot))
                time_used += task_hours
            else:
                unscheduled.append(task)

        reasoning = "\n".join(conflicts) if conflicts else "No conflicts detected."

        self.daily_plan = DailySchedule(
            owner_name=self.owner.name,
            pet_name=pet_name,
            scheduled_tasks=scheduled,
            unscheduled_tasks=unscheduled,
            total_time_used=time_used,
            reasoning=reasoning,
        )
        return self.daily_plan

    def get_plan(self) -> Optional[DailySchedule]:
        """Return the most recently generated schedule."""
        return self.daily_plan

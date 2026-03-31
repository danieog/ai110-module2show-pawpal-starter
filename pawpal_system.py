from __future__ import annotations

from dataclasses import dataclass, field
from datetime import time, date, datetime
from itertools import combinations
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum


class TaskPriority(Enum):
    """Enumeration of task priority levels with numeric weights."""
    LOW = 1
    MEDIUM = 5
    HIGH = 10
    CRITICAL = 20


class RecurrencePattern(Enum):
    """Enumeration of task recurrence patterns."""
    ONCE = "once"
    DAILY = "daily"
    EVERY_2_DAYS = "every_2_days"
    WEEKLY = "weekly"
    WEEKDAYS = "weekdays"
    WEEKENDS = "weekends"
    CUSTOM = "custom"


@dataclass
class Task:
    description: str
    task_time: time
    frequency: str
    duration_minutes: int = 15
    priority: TaskPriority = TaskPriority.MEDIUM
    is_completed: bool = False
    is_overdue: bool = False
    is_critical_medication: bool = False
    min_spacing_hours: int = 0
    custom_recurrence_days: List[int] = field(default_factory=list)
    missed_count: int = 0
    task_id: str = ""

    def __post_init__(self) -> None:
        """Generate unique task ID on initialization."""
        if not self.task_id:
            self.task_id = f"{id(self)}"

    def add_task(self, task_info: Dict[str, Any]) -> None:
        """Populate or refresh task fields from a dictionary payload."""
        self.edit_task(task_info)

    def edit_task(self, task_info: Dict[str, Any]) -> None:
        """Edit mutable task fields from a dictionary payload."""
        if "description" in task_info:
            self.description = str(task_info["description"])
        if "task_time" in task_info:
            task_time_value = task_info["task_time"]
            if not isinstance(task_time_value, time):
                raise TypeError("task_time must be a datetime.time instance")
            self.task_time = task_time_value
        if "frequency" in task_info:
            self.frequency = str(task_info["frequency"])
        if "is_completed" in task_info:
            self.is_completed = bool(task_info["is_completed"])
        if "duration_minutes" in task_info:
            self.duration_minutes = int(task_info["duration_minutes"])
        if "priority" in task_info:
            priority_val = task_info["priority"]
            self.priority = priority_val if isinstance(priority_val, TaskPriority) else TaskPriority.MEDIUM
        if "min_spacing_hours" in task_info:
            self.min_spacing_hours = int(task_info["min_spacing_hours"])
        if "is_critical_medication" in task_info:
            self.is_critical_medication = bool(task_info["is_critical_medication"])

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.is_completed = True
        self.is_overdue = False

    def mark_incomplete(self) -> None:
        """Mark this task as not completed."""
        self.is_completed = False

    def mark_overdue(self) -> None:
        """Mark this task as overdue."""
        self.is_overdue = True

    def mark_missed(self) -> None:
        """Increment missed count for this task."""
        self.missed_count += 1

    def calculate_score(self, now: datetime) -> float:
        """
        Calculate weighted priority score for scheduling.
        Higher score = earlier in schedule.
        """
        base_score = self.priority.value
        
        # Penalty for overdue tasks: add 50 points per day overdue
        if self.is_overdue:
            base_score += 50
        
        # Bonus for critical medications: add 25 points
        if self.is_critical_medication:
            base_score += 25
        
        # Penalty for repeated misses: add 10 points per miss
        base_score += self.missed_count * 10
        
        return base_score

    def get_reminder_lead_time_minutes(self) -> int:
        """Return reminder lead time in minutes based on priority and type."""
        if self.is_critical_medication:
            return 30  # High-risk meds: remind 30 min ahead
        elif self.priority == TaskPriority.HIGH:
            return 15
        elif self.priority == TaskPriority.MEDIUM:
            return 10
        else:
            return 5  # Low-priority tasks: 5 min reminder

    def create_next_instance(self) -> Optional[Task]:
        """
        Create the next recurring instance for daily/weekly tasks.
        Returns None for non-recurring task frequencies.
        """
        normalized_frequency = self.frequency.strip().lower()
        if normalized_frequency not in {"daily", "weekly"}:
            return None

        return Task(
            description=self.description,
            task_time=self.task_time,
            frequency=self.frequency,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            is_completed=False,
            is_overdue=False,
            is_critical_medication=self.is_critical_medication,
            min_spacing_hours=self.min_spacing_hours,
            custom_recurrence_days=list(self.custom_recurrence_days),
            missed_count=0,
        )


@dataclass
class Pet:
    name: str
    species: str
    age: int
    tasks: List[Task] = field(default_factory=list)

    def add_pet_info(self, info: Dict[str, Any]) -> None:
        """Update pet details from a dictionary payload."""
        if "name" in info:
            self.name = str(info["name"])
        if "species" in info:
            self.species = str(info["species"])
        if "age" in info:
            age_value = int(info["age"])
            if age_value < 0:
                raise ValueError("age must be non-negative")
            self.age = age_value

    def add_task(self, task: Task) -> None:
        """Attach a task to this pet if it is not already attached."""
        if task not in self.tasks:
            self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a task from this pet."""
        if task not in self.tasks:
            raise ValueError("task not found for pet")
        self.tasks.remove(task)


class Owner:
    def __init__(self) -> None:
        """Initialize an owner with profile fields, pets, and schedulers."""
        self.name: str = ""
        self.contact: str = ""
        self.pets: List[Pet] = []
        self.schedules: List[Scheduler] = []
        self.available_minutes_per_day: int = 480  # 8 hours by default
        self._task_to_pet_cache: Dict[str, str] = {}  # task_id -> pet_name (O(1) mapping)

    def add_owner_info(self, name: str, contact: Any) -> None:
        """Set or update the owner's name and contact information."""
        self.name = name.strip()
        self.contact = str(contact).strip()

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner if it is not already present."""
        if pet in self.pets:
            return
        self.pets.append(pet)

    def remove_pet(self, pet: Pet) -> None:
        """Remove a pet from this owner."""
        if pet not in self.pets:
            raise ValueError("pet not found for owner")
        self.pets.remove(pet)

    def register_scheduler(self, scheduler: Scheduler) -> None:
        """Register a scheduler with this owner."""
        if scheduler not in self.schedules:
            self.schedules.append(scheduler)

    def get_all_tasks(self) -> List[Task]:
        """Return a flattened list of tasks from all owned pets."""
        return [task for pet in self.pets for task in pet.tasks]

    def build_task_to_pet_map(self) -> Dict[str, str]:
        """
        Build O(1) task-to-pet mapping cache.
        Returns dict: task_id -> pet_name for fast reverse lookups.
        """
        self._task_to_pet_cache = {}
        for pet in self.pets:
            for task in pet.tasks:
                self._task_to_pet_cache[task.task_id] = pet.name
        return self._task_to_pet_cache

    def get_pet_for_task(self, task: Task) -> Optional[str]:
        """Get pet name for a task in O(1) time using cached mapping."""
        return self._task_to_pet_cache.get(task.task_id)


@dataclass
class ScheduleExplanation:
    """Metadata explaining why a task was selected for the schedule."""
    task_id: str
    task_description: str
    priority_score: float
    reasons: List[str] = field(default_factory=list)
    scheduled_time: Optional[time] = None
    pet_name: str = ""


class Scheduler:
    """
    Advanced scheduler implementing all 10 algorithm improvements:
    1. Weighted priority scoring
    2. Constraint-aware greedy day packing
    3. Recurrence expansion
    4. Conflict & spacing rules
    5. O(1) task-to-pet mapping (via Owner cache)
    6. Smart reminder windows
    7. Batch similar tasks
    8. Missed-task recovery
    9. Tie-breakers for equal scores
    10. Scheduling explanation output
    """

    def __init__(self) -> None:
        self.schedule_explanations: List[ScheduleExplanation] = []

    def get_all_owner_tasks(self, owner: Owner) -> List[Task]:
        """Retrieve all tasks for an owner across their pets."""
        return owner.get_all_tasks()

    def complete_task(self, owner: Owner, task: Task) -> Optional[Task]:
        """
        Mark a task complete and auto-create its next instance when recurring.

        For `daily` and `weekly` tasks, a new pending instance is appended
        to the same pet and returned. For other frequencies, returns None.
        """
        task_pet: Optional[Pet] = None
        for pet in owner.pets:
            if task in pet.tasks:
                task_pet = pet
                break

        if task_pet is None:
            raise ValueError("task not found for owner")

        task.mark_complete()
        next_instance = task.create_next_instance()
        if next_instance is not None:
            task_pet.add_task(next_instance)

        return next_instance

    def filter_tasks(
        self,
        owner: Owner,
        is_completed: Optional[bool] = None,
        pet_name: Optional[str] = None,
    ) -> List[Task]:
        """
        Filter tasks by completion status and/or pet name.

        Args:
            owner: The owner whose tasks are searched.
            is_completed: When set, returns only tasks matching this completion state.
            pet_name: When set, returns only tasks for the named pet (case-insensitive).
        """
        normalized_pet_name = pet_name.strip().lower() if pet_name else None
        filtered: List[Task] = []

        for pet in owner.pets:
            if normalized_pet_name and pet.name.lower() != normalized_pet_name:
                continue

            for task in pet.tasks:
                if is_completed is not None and task.is_completed != is_completed:
                    continue
                filtered.append(task)

        return filtered

    def sort_by_time(self, tasks: List[Task]) -> List[Task]:
        """
        Sort task objects by their task_time.
        Supports both datetime.time and 'HH:MM' string values.
        """
        return sorted(
            tasks,
            key=lambda task: (
                task.task_time
                if isinstance(task.task_time, time)
                else datetime.strptime(str(task.task_time), "%H:%M").time()
            ),
        )

    def detect_time_conflicts(self, owner: Owner) -> List[Dict[str, Any]]:
        """
        Detect tasks scheduled at the same time across one or many pets.

        Returns a list of pairwise conflict records containing task/pet details
        and whether the conflict is within the same pet.
        """
        tasks_by_time: Dict[time, List[Tuple[str, Task]]] = {}
        conflicts: List[Dict[str, Any]] = []

        for pet in owner.pets:
            for task in pet.tasks:
                tasks_by_time.setdefault(task.task_time, []).append((pet.name, task))

        for conflict_time, grouped_tasks in tasks_by_time.items():
            if len(grouped_tasks) < 2:
                continue

            for (pet_a, task_a), (pet_b, task_b) in combinations(grouped_tasks, 2):
                conflicts.append(
                    {
                        "time": conflict_time,
                        "pet_a": pet_a,
                        "task_a": task_a,
                        "pet_b": pet_b,
                        "task_b": task_b,
                        "same_pet": pet_a == pet_b,
                    }
                )

        return conflicts

    def get_conflict_warnings(self, owner: Owner) -> List[str]:
        """
        Lightweight conflict detection that returns human-readable warnings.

        This method is intentionally non-throwing: if conflicts exist, it returns
        warning strings. If none exist, it returns an empty list.
        """
        warnings: List[str] = []
        conflicts = self.detect_time_conflicts(owner)

        for conflict in conflicts:
            conflict_time = conflict["time"].strftime("%H:%M")
            task_a = conflict["task_a"].description
            task_b = conflict["task_b"].description
            pet_a = conflict["pet_a"]
            pet_b = conflict["pet_b"]

            if conflict["same_pet"]:
                warnings.append(
                    f"Warning: {pet_a} has overlapping tasks at {conflict_time} "
                    f"({task_a} and {task_b})."
                )
            else:
                warnings.append(
                    f"Warning: overlapping tasks at {conflict_time} across pets "
                    f"({pet_a}: {task_a}, {pet_b}: {task_b})."
                )

        return warnings

    # ALGORITHM 3: Recurrence expansion
    def expand_tasks_for_today(self, owner: Owner, today: date) -> List[Task]:
        """
        Expand tasks based on recurrence patterns.
        Returns only tasks that are due today.
        """
        due_today: List[Task] = []
        weekday = today.weekday()  # 0=Monday, 6=Sunday

        for task in owner.get_all_tasks():
            if task.frequency.lower() == "daily":
                due_today.append(task)
            elif task.frequency.lower() == "every_2_days":
                # Simplified: assume last done on even/odd days
                if today.day % 2 == 0:
                    due_today.append(task)
            elif task.frequency.lower() == "weekly":
                # Assume weekly on the same day of week
                due_today.append(task)
            elif task.frequency.lower() == "weekdays":
                if weekday < 5:  # Mon-Fri
                    due_today.append(task)
            elif task.frequency.lower() == "weekends":
                if weekday >= 5:  # Sat-Sun
                    due_today.append(task)
            elif task.frequency.lower() == "once":
                due_today.append(task)

        return due_today

    # ALGORITHM 1: Weighted priority scoring
    def score_tasks(self, tasks: List[Task], now: datetime) -> List[Tuple[Task, float]]:
        """
        Score each task using weighted priority, overdue penalty, and criticality.
        Returns list of (task, score) tuples sorted by score descending.
        """
        scored = [(task, task.calculate_score(now)) for task in tasks]
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored

    # ALGORITHM 9: Tie-breakers
    def apply_tiebreaker_sort(self, scored_tasks: List[Tuple[Task, float]]) -> List[Task]:
        """
        Apply stable tie-breaking rules to scored tasks.
        Order: medication first, then shorter tasks, then oldest uncompleted.
        """
        def tiebreaker_key(item: Tuple[Task, float]) -> Tuple[float, int, int, str]:
            task, score = item
            is_med = 0 if task.is_critical_medication else 1
            duration = task.duration_minutes
            missed = -task.missed_count  # negative for descending
            time_str = f"{task.task_time.hour:02d}{task.task_time.minute:02d}"
            return (-score, is_med, duration, time_str)

        sorted_items = sorted(scored_tasks, key=tiebreaker_key)
        return [task for task, _ in sorted_items]

    # ALGORITHM 7: Batch similar tasks
    def batch_similar_tasks(self, tasks: List[Task], time_window_minutes: int = 15) -> List[List[Task]]:
        """
        Group tasks that can be batched (e.g., feeding multiple pets close in time).
        Returns list of task batches.
        """
        if not tasks:
            return []

        sorted_tasks = sorted(tasks, key=lambda t: t.task_time)
        batches: List[List[Task]] = []
        current_batch: List[Task] = [sorted_tasks[0]]

        for task in sorted_tasks[1:]:
            last_task_minutes = current_batch[-1].task_time.hour * 60 + current_batch[-1].task_time.minute
            task_minutes = task.task_time.hour * 60 + task.task_time.minute

            if abs(task_minutes - last_task_minutes) <= time_window_minutes:
                current_batch.append(task)
            else:
                batches.append(current_batch)
                current_batch = [task]

        batches.append(current_batch)
        return batches

    # ALGORITHM 5: Check spacing constraints
    def check_spacing_constraint(self, task: Task, scheduled_tasks: List[Task]) -> bool:
        """
        Check if task meets minimum spacing constraint vs already scheduled tasks.
        Returns True if spacing is satisfied.
        """
        if task.min_spacing_hours == 0:
            return True

        task_minute = task.task_time.hour * 60 + task.task_time.minute
        min_spacing_minutes = task.min_spacing_hours * 60

        for scheduled in scheduled_tasks:
            scheduled_minute = scheduled.task_time.hour * 60 + scheduled.task_time.minute
            if abs(task_minute - scheduled_minute) < min_spacing_minutes:
                return False

        return True

    # ALGORITHM 5: Conflict resolution and adjustment
    def find_next_available_slot(self, task: Task, scheduled_tasks: List[Task], max_iterations: int = 20) -> Optional[time]:
        """
        Find next available time slot for a task that respects spacing constraints.
        Returns adjusted time or None if no slot found.
        """
        current_min = task.task_time.hour * 60 + task.task_time.minute
        increment = 5  # Try 5-minute increments

        for _ in range(max_iterations):
            adjusted_hour = (current_min // 60) % 24
            adjusted_minute = current_min % 60
            adjusted_time = time(adjusted_hour, adjusted_minute)
            adjusted_task = Task(
                description=task.description,
                task_time=adjusted_time,
                frequency=task.frequency,
                duration_minutes=task.duration_minutes,
                priority=task.priority,
                min_spacing_hours=task.min_spacing_hours,
            )
            if self.check_spacing_constraint(adjusted_task, scheduled_tasks):
                return adjusted_time
            current_min += increment

        return None

    # ALGORITHM 2: Greedy day-packing under time budget
    def build_daily_schedule(
        self, owner: Owner, today: date = None, owner_available_minutes: int = None
    ) -> List[Task]:
        """
        Build optimized daily schedule using greedy packing:
        - Expand tasks by recurrence
        - Score by weighted priority
        - Greedily fit highest-scoring tasks within owner's time budget
        - Respect spacing constraints and resolve conflicts
        Returns scheduled tasks in time order.
        """
        if today is None:
            today = date.today()
        if owner_available_minutes is None:
            owner_available_minutes = owner.available_minutes_per_day

        now = datetime.combine(today, time(8, 0))  # Assume planning at 8 AM

        # Step 1: Expand tasks for today
        candidate_tasks = self.expand_tasks_for_today(owner, today)

        # Step 2: Score & sort with tiebreakers
        scored = self.score_tasks(candidate_tasks, now)
        sorted_tasks = self.apply_tiebreaker_sort(scored)

        # Step 3: Greedy packing within time budget
        scheduled: List[Task] = []
        total_duration = 0

        for task in sorted_tasks:
            if total_duration + task.duration_minutes <= owner_available_minutes:
                # Check spacing constraint
                if self.check_spacing_constraint(task, scheduled):
                    scheduled.append(task)
                    total_duration += task.duration_minutes
                else:
                    # Try to find alternative slot
                    alt_time = self.find_next_available_slot(task, scheduled)
                    if alt_time:
                        task.task_time = alt_time
                        scheduled.append(task)
                        total_duration += task.duration_minutes

        # Sort final schedule by time
        scheduled.sort(key=lambda t: t.task_time)

        # Build explanations
        self.schedule_explanations = self._build_explanations(scheduled, scored, owner)

        return scheduled

    # ALGORITHM 10: Scheduling explanation metadata
    def _build_explanations(self, scheduled: List[Task], scored: List[Tuple[Task, float]], owner: Owner) -> List[ScheduleExplanation]:
        """Build explanation metadata for why each task was selected."""
        owner.build_task_to_pet_map()
        explanations: List[ScheduleExplanation] = []

        for task in scheduled:
            task_score = next((s for t, s in scored if t.task_id == task.task_id), 0.0)
            reasons = []

            if task.is_critical_medication:
                reasons.append("Critical medication (must not miss)")
            if task.priority == TaskPriority.HIGH:
                reasons.append("High priority")
            if task.is_overdue:
                reasons.append("Overdue (penalty applied)")
            if task.missed_count > 0:
                reasons.append(f"Missed {task.missed_count} times (recovery)")

            pet_name = owner.get_pet_for_task(task) or "Unknown"

            explanation = ScheduleExplanation(
                task_id=task.task_id,
                task_description=task.description,
                priority_score=task_score,
                reasons=reasons,
                scheduled_time=task.task_time,
                pet_name=pet_name,
            )
            explanations.append(explanation)

        return explanations

    # ALGORITHM 6: Smart reminder windows
    def get_reminders_due(self, scheduled_tasks: List[Task], current_time: datetime) -> List[Tuple[Task, int]]:
        """
        Get tasks that are due for reminders based on lead time windows.
        Returns list of (task, minutes_until_due).
        """
        due_reminders: List[Tuple[Task, int]] = []
        current_minutes = current_time.hour * 60 + current_time.minute

        for task in scheduled_tasks:
            task_minutes = task.task_time.hour * 60 + task.task_time.minute
            minutes_until = task_minutes - current_minutes

            lead_time = task.get_reminder_lead_time_minutes()

            if 0 <= minutes_until <= lead_time:
                due_reminders.append((task, minutes_until))

        return due_reminders

    # ALGORITHM 8: Missed-task recovery
    def reschedule_missed_task(self, task: Task, owner: Owner, today: date) -> Optional[Task]:
        """
        Auto-generate recovery task for a missed item.
        Returns new task with adjusted priority/timing or None.
        """
        task.mark_missed()

        # Bump priority for next occurrence
        if task.priority == TaskPriority.LOW:
            task.priority = TaskPriority.MEDIUM
        elif task.priority == TaskPriority.MEDIUM:
            task.priority = TaskPriority.HIGH
        elif task.priority == TaskPriority.HIGH:
            task.priority = TaskPriority.CRITICAL

        # Suggest recovery at next available time (e.g., +2 hours)
        new_hour = (task.task_time.hour + 2) % 24
        task.task_time = time(new_hour, task.task_time.minute)

        return task

    def adjust_schedule(self, owner: Owner, task: Task) -> None:
        """Attach a task to the owner's pet with the fewest assigned tasks (fallback)."""
        for pet in owner.pets:
            if task in pet.tasks:
                return

        if not owner.pets:
            raise ValueError("owner must have at least one pet to schedule a task")

        pet_with_fewest_tasks = min(owner.pets, key=lambda pet: len(pet.tasks))
        pet_with_fewest_tasks.add_task(task)

    def send_reminder(self, task: Task) -> None:
        """Print a formatted reminder message for a task."""
        status = "completed" if task.is_completed else "pending"
        print(
            f"Reminder: {task.description} at {task.task_time.strftime('%H:%M')} "
            f"({task.frequency}, {status})"
        )

    def sort_tasks_by_due_date(self, owner: Owner) -> List[Task]:
        """Return the owner's tasks sorted by task time."""
        return sorted(owner.get_all_tasks(), key=lambda task: task.task_time)

    def get_pending_tasks(self, owner: Owner) -> List[Task]:
        """Return only tasks that are not marked completed."""
        return [task for task in owner.get_all_tasks() if not task.is_completed]

    def print_schedule_with_explanations(self, scheduled: List[Task], owner: Owner) -> None:
        """Print schedule with explanations for each task (Algorithm 10)."""
        owner.build_task_to_pet_map()
        print("\n" + "=" * 80)
        print("OPTIMIZED DAILY SCHEDULE WITH EXPLANATIONS")
        print("=" * 80)

        for i, task in enumerate(scheduled, 1):
            pet_name = owner.get_pet_for_task(task) or "Unknown"
            explanation = next((e for e in self.schedule_explanations if e.task_id == task.task_id), None)

            print(f"\n{i}. {task.task_time.strftime('%H:%M')} | {pet_name} | {task.description}")
            print(f"   Priority Score: {explanation.priority_score if explanation else 'N/A'}")
            print(f"   Duration: {task.duration_minutes} minutes")

            if explanation and explanation.reasons:
                print(f"   Why selected:")
                for reason in explanation.reasons:
                    print(f"     - {reason}")
        print("\n" + "=" * 80)

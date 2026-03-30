from __future__ import annotations

from dataclasses import dataclass, field
from datetime import time
from typing import Any, Dict, List


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


@dataclass
class Task:
    description: str
    task_time: time
    frequency: str
    is_completed: bool = False

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

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.is_completed = True

    def mark_incomplete(self) -> None:
        """Mark this task as not completed."""
        self.is_completed = False


class Owner:
    def __init__(self) -> None:
        """Initialize an owner with profile fields, pets, and schedulers."""
        self.name: str = ""
        self.contact: str = ""
        self.pets: List[Pet] = []
        self.schedules: List[Scheduler] = []

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


class Scheduler:
    def get_all_owner_tasks(self, owner: Owner) -> List[Task]:
        """Retrieve all tasks for an owner across their pets."""
        return owner.get_all_tasks()

    def adjust_schedule(self, owner: Owner, task: Task) -> None:
        """Attach a task to the owner's pet with the fewest assigned tasks."""
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

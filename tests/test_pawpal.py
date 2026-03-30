from datetime import time

from pawpal_system import Pet, Task


def test_task_completion_marks_task_complete() -> None:
    task = Task(description="Morning walk", task_time=time(8, 0), frequency="Daily")

    assert task.is_completed is False
    task.mark_complete()
    assert task.is_completed is True


def test_pet_task_addition_increases_task_count() -> None:
    pet = Pet(name="Luna", species="Dog", age=4)
    task = Task(description="Breakfast", task_time=time(9, 0), frequency="Daily")

    initial_count = len(pet.tasks)
    pet.add_task(task)

    assert len(pet.tasks) == initial_count + 1

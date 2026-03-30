from datetime import time

from pawpal_system import Owner, Pet, Scheduler, Task


def print_todays_schedule(owner: Owner, scheduler: Scheduler) -> None:
	print("Today's Schedule")
	print("=" * 16)

	sorted_tasks = scheduler.sort_tasks_by_due_date(owner)
	for task in sorted_tasks:
		pet_name = "Unknown Pet"
		for pet in owner.pets:
			if task in pet.tasks:
				pet_name = pet.name
				break

		print(
			f"{task.task_time.strftime('%H:%M')} | {pet_name} | "
			f"{task.description} ({task.frequency})"
		)


def main() -> None:
	owner = Owner()
	owner.add_owner_info("Alex Rivera", "alex@email.com")

	luna = Pet(name="Luna", species="Dog", age=4)
	milo = Pet(name="Milo", species="Cat", age=2)
	owner.add_pet(luna)
	owner.add_pet(milo)

	morning_walk = Task(
		description="Morning walk",
		task_time=time(8, 0),
		frequency="Daily",
	)
	breakfast = Task(
		description="Breakfast feeding",
		task_time=time(9, 0),
		frequency="Daily",
	)
	evening_med = Task(
		description="Evening medication",
		task_time=time(19, 30),
		frequency="Daily",
	)

	luna.add_task(morning_walk)
	luna.add_task(evening_med)
	milo.add_task(breakfast)

	scheduler = Scheduler()
	owner.register_scheduler(scheduler)

	print_todays_schedule(owner, scheduler)


if __name__ == "__main__":
	main()

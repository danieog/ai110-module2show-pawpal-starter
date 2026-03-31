from datetime import date, datetime, time

from pawpal_system import Owner, Pet, Scheduler, Task, TaskPriority


def print_todays_schedule(owner: Owner, scheduler: Scheduler) -> None:
    """Print today's schedule using only simple time sort (old behavior)."""
    print("Today's Schedule (Simple Time Sort)")
    print("=" * 40)

    sorted_tasks = scheduler.sort_tasks_by_due_date(owner)
    owner.build_task_to_pet_map()  # Build O(1) cache

    for task in sorted_tasks:
        pet_name = owner.get_pet_for_task(task) or "Unknown Pet"
        print(
            f"{task.task_time.strftime('%H:%M')} | {pet_name} | "
            f"{task.description} ({task.frequency})"
        )


def print_optimized_schedule(owner: Owner, scheduler: Scheduler) -> None:
    """Print optimized schedule with intelligent ordering and explanations."""
    scheduled = scheduler.build_daily_schedule(owner)
    scheduler.print_schedule_with_explanations(scheduled, owner)


def print_reminders(owner: Owner, scheduler: Scheduler, current_time: datetime) -> None:
    """Print active reminders for tasks (Algorithm 6)."""
    scheduled = scheduler.build_daily_schedule(owner)
    reminders = scheduler.get_reminders_due(scheduled, current_time)

    if reminders:
        print("\n" + "=" * 80)
        print("ACTIVE REMINDERS")
        print("=" * 80)
        for task, minutes_until in reminders:
            pet_name = owner.get_pet_for_task(task) or "Unknown"
            print(f"Reminder | {pet_name}: {task.description}")
            print(f"   Due in {minutes_until} minutes at {task.task_time.strftime('%H:%M')}")
    else:
        print("\nNo active reminders at this time.")


def print_batched_tasks(owner: Owner, scheduler: Scheduler) -> None:
    """Print tasks grouped by batches (Algorithm 7)."""
    all_tasks = owner.get_all_tasks()
    batches = scheduler.batch_similar_tasks(all_tasks, time_window_minutes=15)

    print("\n" + "=" * 80)
    print("TASK BATCHES (Grouped by Time Proximity)")
    print("=" * 80)
    owner.build_task_to_pet_map()

    for i, batch in enumerate(batches, 1):
        print(f"\nBatch {i}:")
        for task in batch:
            pet_name = owner.get_pet_for_task(task) or "Unknown"
            print(
                f"  {task.task_time.strftime('%H:%M')} | {pet_name} | "
                f"{task.description} ({task.duration_minutes}m)"
            )


def main() -> None:
    owner = Owner()
    owner.add_owner_info("Alex Rivera", "alex@email.com")
    owner.available_minutes_per_day = 120  # 2 hours available

    # Create pets
    luna = Pet(name="Luna", species="Dog", age=4)
    milo = Pet(name="Milo", species="Cat", age=2)
    owner.add_pet(luna)
    owner.add_pet(milo)

    # ===== Task Creation with New Features =====
    morning_walk = Task(
        description="Morning walk",
        task_time=time(8, 0),
        frequency="Daily",
        duration_minutes=20,
        priority=TaskPriority.HIGH,
    )

    morning_med = Task(
        description="Morning medication",
        task_time=time(8, 30),
        frequency="Daily",
        duration_minutes=5,
        priority=TaskPriority.CRITICAL,
        is_critical_medication=True,
        min_spacing_hours=12,
    )

    breakfast = Task(
        description="Breakfast feeding",
        task_time=time(9, 0),
        frequency="Daily",
        duration_minutes=15,
        priority=TaskPriority.HIGH,
    )

    breakfast_refill = Task(
        description="Breakfast refill",
        task_time=time(9, 0),
        frequency="Daily",
        duration_minutes=10,
        priority=TaskPriority.MEDIUM,
    )

    grooming = Task(
        description="Grooming session",
        task_time=time(14, 0),
        frequency="weekdays",
        duration_minutes=30,
        priority=TaskPriority.MEDIUM,
    )

    evening_med = Task(
        description="Evening medication",
        task_time=time(19, 30),
        frequency="Daily",
        duration_minutes=5,
        priority=TaskPriority.CRITICAL,
        is_critical_medication=True,
        min_spacing_hours=12,
    )

    missed_earlier = Task(
        description="Lunch feeding",
        task_time=time(12, 0),
        frequency="Daily",
        duration_minutes=10,
        priority=TaskPriority.MEDIUM,
    )
    missed_earlier.mark_missed()
    missed_earlier.mark_missed()

    play_time = Task(
        description="Playtime and enrichment",
        task_time=time(15, 30),
        frequency="Daily",
        duration_minutes=20,
        priority=TaskPriority.LOW,
    )

    # Intentionally add tasks out of chronological order.
    luna.add_task(evening_med)
    luna.add_task(morning_walk)
    luna.add_task(morning_med)
    luna.add_task(breakfast_refill)

    milo.add_task(play_time)
    milo.add_task(breakfast)
    milo.add_task(grooming)
    milo.add_task(missed_earlier)

    # Mark one task complete so completion filtering has visible output.
    breakfast.mark_complete()

    scheduler = Scheduler()
    owner.register_scheduler(scheduler)

    print("\n" + "=" * 80)
    print("PAWPAL+ SCHEDULING SYSTEM - ALL 10 ALGORITHMS DEMONSTRATED")
    print("=" * 80)

    print("\n" + "=" * 80)
    print("OUT-OF-ORDER INPUT (RAW)")
    print("=" * 80)
    owner.build_task_to_pet_map()
    for task in owner.get_all_tasks():
        pet_name = owner.get_pet_for_task(task) or "Unknown"
        print(f"  {task.task_time.strftime('%H:%M')} | {pet_name} | {task.description}")

    print("\n" + "=" * 80)
    print("SORTED WITH Scheduler.sort_by_time")
    print("=" * 80)
    for task in scheduler.sort_by_time(owner.get_all_tasks()):
        pet_name = owner.get_pet_for_task(task) or "Unknown"
        print(f"  {task.task_time.strftime('%H:%M')} | {pet_name} | {task.description}")

    print("\n" + "=" * 80)
    print("FILTERED WITH Scheduler.filter_tasks")
    print("=" * 80)
    completed_tasks = scheduler.filter_tasks(owner, is_completed=True)
    luna_tasks = scheduler.filter_tasks(owner, pet_name="Luna")
    luna_pending = scheduler.filter_tasks(owner, is_completed=False, pet_name="Luna")

    print("Completed tasks:")
    for task in completed_tasks:
        pet_name = owner.get_pet_for_task(task) or "Unknown"
        print(f"  {task.task_time.strftime('%H:%M')} | {pet_name} | {task.description}")

    print("Luna tasks (all statuses):")
    for task in luna_tasks:
        print(f"  {task.task_time.strftime('%H:%M')} | Luna | {task.description}")

    print("Luna pending tasks:")
    for task in luna_pending:
        print(f"  {task.task_time.strftime('%H:%M')} | Luna | {task.description}")

    print("\n" + "=" * 80)
    print("LIGHTWEIGHT CONFLICT WARNINGS")
    print("=" * 80)
    warnings = scheduler.get_conflict_warnings(owner)
    if warnings:
        for warning in warnings:
            print(warning)
    else:
        print("No conflicts detected.")

    print_todays_schedule(owner, scheduler)
    print_optimized_schedule(owner, scheduler)
    print_batched_tasks(owner, scheduler)

    print("\n--- Simulating Current Time: 18:50 ---")
    current_time = datetime(2024, 1, 15, 18, 50)
    print_reminders(owner, scheduler, current_time)

    print("\n" + "=" * 80)
    print("RECURRENCE EXPANSION (Algorithm 3)")
    print("=" * 80)
    today = date.today()
    due_today = scheduler.expand_tasks_for_today(owner, today)
    print(f"Tasks due today ({today.strftime('%A, %B %d')}):")
    owner.build_task_to_pet_map()
    for task in sorted(due_today, key=lambda t: t.task_time):
        pet_name = owner.get_pet_for_task(task) or "Unknown"
        print(f"  {task.task_time.strftime('%H:%M')} | {pet_name} | {task.description}")

    print("\n" + "=" * 80)
    print("MISSED TASK RECOVERY (Algorithm 8)")
    print("=" * 80)
    print(f"Lunch feeding missed {missed_earlier.missed_count} times")
    print("Original priority: MEDIUM (5 points)")
    print(
        "After misses, priority escalates to: "
        f"{missed_earlier.priority.name} ({missed_earlier.priority.value} points)"
    )

    print("\n" + "=" * 80)
    print("SPACING CONSTRAINT CHECKING (Algorithm 5)")
    print("=" * 80)
    print(f"Morning med at {morning_med.task_time.strftime('%H:%M')}")
    print(f"Evening med at {evening_med.task_time.strftime('%H:%M')}")
    print(f"Min spacing required: {morning_med.min_spacing_hours} hours")
    diff_hours = (evening_med.task_time.hour - morning_med.task_time.hour) % 24
    is_valid = diff_hours >= morning_med.min_spacing_hours
    print(f"Spacing valid: {is_valid} [OK]" if is_valid else f"Spacing valid: {is_valid} [FAIL]")


if __name__ == "__main__":
    main()

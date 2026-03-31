from datetime import time, date, datetime

from pawpal_system import Owner, Pet, Scheduler, Task, TaskPriority


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


# ==================== ALGORITHM 1: Weighted Priority Scoring ====================

def test_priority_scoring_critical_medication_highest() -> None:
    """Algorithm 1: Critical meds should score higher than low-priority tasks."""
    med_task = Task(
        description="Evening medication",
        task_time=time(19, 0),
        frequency="Daily",
        priority=TaskPriority.LOW,
        is_critical_medication=True,
    )
    play_task = Task(
        description="Playtime",
        task_time=time(15, 0),
        frequency="Daily",
        priority=TaskPriority.HIGH,
    )

    now = datetime.now()
    med_score = med_task.calculate_score(now)
    play_score = play_task.calculate_score(now)

    assert med_score > play_score, "Critical meds should score higher"


def test_priority_scoring_overdue_penalty() -> None:
    """Algorithm 1: Overdue tasks get penalty boost."""
    task_on_time = Task(
        description="Morning walk",
        task_time=time(8, 0),
        frequency="Daily",
        priority=TaskPriority.MEDIUM,
    )
    task_overdue = Task(
        description="Missed medication",
        task_time=time(8, 0),
        frequency="Daily",
        priority=TaskPriority.MEDIUM,
        is_overdue=True,
    )

    now = datetime.now()
    on_time_score = task_on_time.calculate_score(now)
    overdue_score = task_overdue.calculate_score(now)

    assert overdue_score > on_time_score, "Overdue tasks should score higher"


def test_priority_scoring_missed_count_penalty() -> None:
    """Algorithm 1: Repeated misses increase priority score."""
    task = Task(
        description="Feeding",
        task_time=time(9, 0),
        frequency="Daily",
        priority=TaskPriority.MEDIUM,
    )

    now = datetime.now()
    initial_score = task.calculate_score(now)

    task.mark_missed()
    task.mark_missed()

    missed_score = task.calculate_score(now)
    assert missed_score > initial_score


# ==================== ALGORITHM 3: Recurrence Expansion ====================

def test_recurrence_expansion_daily_tasks() -> None:
    """Algorithm 3: Daily tasks should be due today."""
    scheduler = Scheduler()
    owner = Owner()
    pet = Pet(name="Luna", species="Dog", age=4)
    owner.add_pet(pet)

    daily_task = Task(
        description="Morning walk",
        task_time=time(8, 0),
        frequency="Daily",
    )
    pet.add_task(daily_task)

    today = date.today()
    due_tasks = scheduler.expand_tasks_for_today(owner, today)

    assert daily_task in due_tasks


def test_recurrence_expansion_weekday_tasks() -> None:
    """Algorithm 3: Weekday tasks only on weekdays (Mon-Fri)."""
    scheduler = Scheduler()
    owner = Owner()
    pet = Pet(name="Luna", species="Dog", age=4)
    owner.add_pet(pet)

    weekday_task = Task(
        description="Weekday medication",
        task_time=time(9, 0),
        frequency="weekdays",
    )
    pet.add_task(weekday_task)

    today = date.today()
    due_tasks = scheduler.expand_tasks_for_today(owner, today)

    if today.weekday() < 5:  # Mon-Fri
        assert weekday_task in due_tasks
    else:  # Sat-Sun
        assert weekday_task not in due_tasks


# ==================== ALGORITHM 4 & 5: Spacing Constraints ====================

def test_spacing_constraint_check() -> None:
    """Algorithm 5: Spacing between same-type tasks should be enforced."""
    scheduler = Scheduler()
    
    med1 = Task(
        description="Morning medication",
        task_time=time(8, 0),
        frequency="Daily",
        min_spacing_hours=8,
    )
    med2 = Task(
        description="Evening medication",
        task_time=time(9, 0),
        frequency="Daily",
        min_spacing_hours=8,
    )

    scheduled = [med1]
    
    # med2 is only 1 hour away, should fail spacing check
    is_valid = scheduler.check_spacing_constraint(med2, scheduled)
    assert is_valid is False, "Spacing constraint should prevent tasks < 8h apart"


def test_spacing_constraint_sufficient_gap() -> None:
    """Algorithm 5: Tasks with sufficient gap should pass constraint check."""
    scheduler = Scheduler()
    
    med1 = Task(
        description="Morning medication",
        task_time=time(8, 0),
        frequency="Daily",
        min_spacing_hours=8,
    )
    med2 = Task(
        description="Evening medication",
        task_time=time(16, 30),
        frequency="Daily",
        min_spacing_hours=8,
    )

    scheduled = [med1]
    
    # med2 is > 8 hours away, should pass
    is_valid = scheduler.check_spacing_constraint(med2, scheduled)
    assert is_valid is True


# ==================== ALGORITHM 2: Greedy Day Packing ====================

def test_greedy_packing_respects_time_budget() -> None:
    """Algorithm 2: Schedule should not exceed owner's available time budget."""
    scheduler = Scheduler()
    owner = Owner()
    owner.available_minutes_per_day = 60  # Only 1 hour available
    
    pet = Pet(name="Luna", species="Dog", age=4)
    owner.add_pet(pet)

    # Add 3 tasks @ 30 min each = 90 min total
    for i in range(3):
        task = Task(
            description=f"Task {i+1}",
            task_time=time(8 + i, 0),
            frequency="Daily",
            duration_minutes=30,
            priority=TaskPriority.MEDIUM,
        )
        pet.add_task(task)

    scheduled = scheduler.build_daily_schedule(owner, owner_available_minutes=60)

    total_duration = sum(t.duration_minutes for t in scheduled)
    assert total_duration <= 60, f"Total duration {total_duration}m exceeds budget"


def test_greedy_packing_prioritizes_high_value() -> None:
    """Algorithm 2: High-priority tasks should be selected before low-priority."""
    scheduler = Scheduler()
    owner = Owner()
    owner.available_minutes_per_day = 35  # Only 35 min (enough for one 30min task)
    
    pet = Pet(name="Luna", species="Dog", age=4)
    owner.add_pet(pet)

    high_prio = Task(
        description="Critical medication",
        task_time=time(8, 0),
        frequency="Daily",
        duration_minutes=30,
        priority=TaskPriority.CRITICAL,
    )
    low_prio = Task(
        description="Playtime",
        task_time=time(9, 0),
        frequency="Daily",
        duration_minutes=30,
        priority=TaskPriority.LOW,
    )
    pet.add_task(high_prio)
    pet.add_task(low_prio)

    scheduled = scheduler.build_daily_schedule(owner)

    assert high_prio in scheduled, "High-priority task should be selected"
    assert low_prio not in scheduled, "Low-priority task should be skipped under budget"


# ==================== ALGORITHM 7: Batch Similar Tasks ====================

def test_batch_similar_tasks_groups_close_times() -> None:
    """Algorithm 7: Tasks within time window should be batched."""
    scheduler = Scheduler()
    
    task1 = Task(description="Feed Luna", task_time=time(9, 0), frequency="Daily")
    task2 = Task(description="Feed Milo", task_time=time(9, 10), frequency="Daily")
    task3 = Task(description="Playtime", task_time=time(10, 0), frequency="Daily")

    tasks = [task1, task2, task3]
    batches = scheduler.batch_similar_tasks(tasks, time_window_minutes=15)

    assert len(batches) == 2, "Should create 2 batches (feed group + playtime)"
    assert task1 in batches[0] and task2 in batches[0], "Feed tasks should be batched"


# ==================== ALGORITHM 4 & 5: Task-to-Pet Mapping ====================

def test_task_to_pet_mapping_o1_lookup() -> None:
    """Algorithm 4: Task-to-pet cache should enable O(1) lookups."""
    owner = Owner()
    
    luna = Pet(name="Luna", species="Dog", age=4)
    milo = Pet(name="Milo", species="Cat", age=2)
    owner.add_pet(luna)
    owner.add_pet(milo)

    walk_task = Task(description="Morning walk", task_time=time(8, 0), frequency="Daily")
    feed_task = Task(description="Breakfast", task_time=time(9, 0), frequency="Daily")

    luna.add_task(walk_task)
    milo.add_task(feed_task)

    # Build cache
    cache = owner.build_task_to_pet_map()

    # O(1) lookups should work
    assert owner.get_pet_for_task(walk_task) == "Luna"
    assert owner.get_pet_for_task(feed_task) == "Milo"


# ==================== ALGORITHM 6: Smart Reminders ====================

def test_smart_reminder_windows() -> None:
    """Algorithm 6: Reminders should trigger based on lead time windows."""
    scheduler = Scheduler()
    
    med = Task(
        description="Evening medication",
        task_time=time(19, 0),
        frequency="Daily",
        priority=TaskPriority.CRITICAL,
        is_critical_medication=True,
    )

    # At 18:30, medication is 30 min away
    current = datetime(2024, 1, 1, 18, 30)
    reminders = scheduler.get_reminders_due([med], current)

    # Critical meds have 30 min lead time, so should trigger
    assert len(reminders) > 0, "Reminder should trigger 30 min before critical med"


def test_smart_reminder_different_lead_times() -> None:
    """Algorithm 6: Lead time should vary by priority."""
    low_prio_task = Task(
        description="Playtime",
        task_time=time(15, 0),
        frequency="Daily",
        priority=TaskPriority.LOW,
    )
    high_prio_task = Task(
        description="High-priority task",
        task_time=time(15, 0),
        frequency="Daily",
        priority=TaskPriority.HIGH,
    )

    low_lead = low_prio_task.get_reminder_lead_time_minutes()
    high_lead = high_prio_task.get_reminder_lead_time_minutes()

    assert low_lead < high_lead, "Low-priority tasks should have shorter lead times"


# ==================== ALGORITHM 8: Missed-Task Recovery ====================

def test_missed_task_recovery_escalates_priority() -> None:
    """Algorithm 8: Missed tasks should get priority boost."""
    task = Task(
        description="Medication",
        task_time=time(8, 0),
        frequency="Daily",
        priority=TaskPriority.MEDIUM,
    )

    initial_priority = task.priority
    scheduler = Scheduler()
    scheduler.reschedule_missed_task(task, Owner(), date.today())

    assert task.priority.value > initial_priority.value, "Missed task priority should escalate"
    assert task.missed_count == 1


# ==================== ALGORITHM 9: Tie-Breakers ====================

def test_tiebreaker_medications_first() -> None:
    """Algorithm 9: When scores tie, medications should come before play."""
    scheduler = Scheduler()
    
    med = Task(
        description="Medication",
        task_time=time(9, 0),
        frequency="Daily",
        priority=TaskPriority.MEDIUM,
        is_critical_medication=True,
        duration_minutes=10,
    )
    play = Task(
        description="Playtime",
        task_time=time(9, 0),
        frequency="Daily",
        priority=TaskPriority.MEDIUM,
        duration_minutes=10,
    )

    scored = [(med, 10.0), (play, 10.0)]  # Same score
    sorted_tasks = scheduler.apply_tiebreaker_sort(scored)

    assert sorted_tasks[0] == med, "Medication should come first in tie-breaker"


def test_tiebreaker_shorter_tasks_first() -> None:
    """Algorithm 9: Among equal non-med tasks, shorter should come first."""
    scheduler = Scheduler()
    
    short_task = Task(
        description="Quick walk",
        task_time=time(9, 0),
        frequency="Daily",
        priority=TaskPriority.MEDIUM,
        duration_minutes=15,
    )
    long_task = Task(
        description="Long session",
        task_time=time(9, 0),
        frequency="Daily",
        priority=TaskPriority.MEDIUM,
        duration_minutes=60,
    )

    scored = [(short_task, 5.0), (long_task, 5.0)]  # Same score
    sorted_tasks = scheduler.apply_tiebreaker_sort(scored)

    assert sorted_tasks[0] == short_task, "Shorter task should come first"


# ==================== ALGORITHM 10: Scheduling Explanations ====================

def test_scheduling_explanation_metadata() -> None:
    """Algorithm 10: Scheduled tasks should have explanation metadata."""
    scheduler = Scheduler()
    owner = Owner()
    
    pet = Pet(name="Luna", species="Dog", age=4)
    owner.add_pet(pet)

    med = Task(
        description="Evening medication",
        task_time=time(19, 0),
        frequency="Daily",
        priority=TaskPriority.HIGH,
        is_critical_medication=True,
        duration_minutes=5,
    )
    pet.add_task(med)

    scheduled = scheduler.build_daily_schedule(owner)

    assert len(scheduler.schedule_explanations) > 0, "Explanations should be generated"
    explanation = scheduler.schedule_explanations[0]
    assert any("Critical medication" in reason for reason in explanation.reasons)
    assert explanation.pet_name == "Luna"


def test_explanation_reasons_populated() -> None:
    """Algorithm 10: Explanation reasons should reflect why task was selected."""
    scheduler = Scheduler()
    owner = Owner()
    
    pet = Pet(name="Milo", species="Cat", age=2)
    owner.add_pet(pet)

    overdue_med = Task(
        description="Missed morning medication",
        task_time=time(8, 0),
        frequency="Daily",
        priority=TaskPriority.HIGH,
        is_overdue=True,
        is_critical_medication=True,
        duration_minutes=5,
    )
    pet.add_task(overdue_med)

    scheduler.build_daily_schedule(owner)

    explanation = next((e for e in scheduler.schedule_explanations if e.task_description == "Missed morning medication"), None)
    assert explanation is not None
    reasons_text = " ".join(explanation.reasons)
    assert "Overdue" in reasons_text or "Critical" in reasons_text


def test_filter_tasks_by_completion_status() -> None:
    scheduler = Scheduler()
    owner = Owner()
    pet = Pet(name="Luna", species="Dog", age=4)
    owner.add_pet(pet)

    done_task = Task(description="Done task", task_time=time(8, 0), frequency="Daily")
    pending_task = Task(description="Pending task", task_time=time(9, 0), frequency="Daily")
    done_task.mark_complete()

    pet.add_task(done_task)
    pet.add_task(pending_task)

    completed = scheduler.filter_tasks(owner, is_completed=True)
    pending = scheduler.filter_tasks(owner, is_completed=False)

    assert done_task in completed
    assert pending_task not in completed
    assert pending_task in pending
    assert done_task not in pending


def test_filter_tasks_by_pet_name() -> None:
    scheduler = Scheduler()
    owner = Owner()

    luna = Pet(name="Luna", species="Dog", age=4)
    milo = Pet(name="Milo", species="Cat", age=2)
    owner.add_pet(luna)
    owner.add_pet(milo)

    luna_task = Task(description="Walk", task_time=time(8, 0), frequency="Daily")
    milo_task = Task(description="Feed", task_time=time(9, 0), frequency="Daily")
    luna.add_task(luna_task)
    milo.add_task(milo_task)

    luna_tasks = scheduler.filter_tasks(owner, pet_name="luna")

    assert luna_task in luna_tasks
    assert milo_task not in luna_tasks


def test_complete_task_creates_next_daily_instance() -> None:
    scheduler = Scheduler()
    owner = Owner()
    pet = Pet(name="Luna", species="Dog", age=4)
    owner.add_pet(pet)

    daily_task = Task(description="Morning walk", task_time=time(8, 0), frequency="daily")
    pet.add_task(daily_task)

    next_task = scheduler.complete_task(owner, daily_task)

    assert daily_task.is_completed is True
    assert next_task is not None
    assert next_task in pet.tasks
    assert next_task is not daily_task
    assert next_task.is_completed is False
    assert next_task.description == daily_task.description
    assert next_task.task_time == daily_task.task_time


def test_complete_task_creates_next_weekly_instance() -> None:
    scheduler = Scheduler()
    owner = Owner()
    pet = Pet(name="Milo", species="Cat", age=2)
    owner.add_pet(pet)

    weekly_task = Task(description="Weekly grooming", task_time=time(10, 0), frequency="weekly")
    pet.add_task(weekly_task)

    next_task = scheduler.complete_task(owner, weekly_task)

    assert weekly_task.is_completed is True
    assert next_task is not None
    assert next_task in pet.tasks
    assert next_task.frequency.lower() == "weekly"
    assert next_task.is_completed is False


def test_complete_task_does_not_rollover_non_recurring() -> None:
    scheduler = Scheduler()
    owner = Owner()
    pet = Pet(name="Luna", species="Dog", age=4)
    owner.add_pet(pet)

    one_time_task = Task(description="Vet visit", task_time=time(13, 0), frequency="once")
    pet.add_task(one_time_task)
    initial_count = len(pet.tasks)

    next_task = scheduler.complete_task(owner, one_time_task)

    assert one_time_task.is_completed is True
    assert next_task is None
    assert len(pet.tasks) == initial_count


def test_detect_time_conflicts_same_pet() -> None:
    scheduler = Scheduler()
    owner = Owner()
    luna = Pet(name="Luna", species="Dog", age=4)
    owner.add_pet(luna)

    walk = Task(description="Walk", task_time=time(8, 0), frequency="Daily")
    meds = Task(description="Meds", task_time=time(8, 0), frequency="Daily")
    luna.add_task(walk)
    luna.add_task(meds)

    conflicts = scheduler.detect_time_conflicts(owner)

    assert len(conflicts) == 1
    assert conflicts[0]["same_pet"] is True
    assert conflicts[0]["pet_a"] == "Luna"
    assert conflicts[0]["pet_b"] == "Luna"


def test_detect_time_conflicts_different_pets() -> None:
    scheduler = Scheduler()
    owner = Owner()
    luna = Pet(name="Luna", species="Dog", age=4)
    milo = Pet(name="Milo", species="Cat", age=2)
    owner.add_pet(luna)
    owner.add_pet(milo)

    luna_task = Task(description="Luna breakfast", task_time=time(9, 0), frequency="Daily")
    milo_task = Task(description="Milo breakfast", task_time=time(9, 0), frequency="Daily")
    luna.add_task(luna_task)
    milo.add_task(milo_task)

    conflicts = scheduler.detect_time_conflicts(owner)

    assert len(conflicts) == 1
    assert conflicts[0]["same_pet"] is False
    assert {conflicts[0]["pet_a"], conflicts[0]["pet_b"]} == {"Luna", "Milo"}


def test_detect_time_conflicts_none() -> None:
    scheduler = Scheduler()
    owner = Owner()
    luna = Pet(name="Luna", species="Dog", age=4)
    owner.add_pet(luna)

    morning = Task(description="Morning walk", task_time=time(8, 0), frequency="Daily")
    evening = Task(description="Evening walk", task_time=time(18, 0), frequency="Daily")
    luna.add_task(morning)
    luna.add_task(evening)

    conflicts = scheduler.detect_time_conflicts(owner)

    assert conflicts == []


def test_get_conflict_warnings_returns_messages() -> None:
    scheduler = Scheduler()
    owner = Owner()
    luna = Pet(name="Luna", species="Dog", age=4)
    owner.add_pet(luna)

    task1 = Task(description="Morning walk", task_time=time(8, 0), frequency="Daily")
    task2 = Task(description="Breakfast", task_time=time(8, 0), frequency="Daily")
    luna.add_task(task1)
    luna.add_task(task2)

    warnings = scheduler.get_conflict_warnings(owner)

    assert len(warnings) == 1
    assert warnings[0].startswith("Warning:")
    assert "08:00" in warnings[0]


def test_get_conflict_warnings_empty_when_no_conflicts() -> None:
    scheduler = Scheduler()
    owner = Owner()
    milo = Pet(name="Milo", species="Cat", age=2)
    owner.add_pet(milo)

    task1 = Task(description="Morning feed", task_time=time(8, 0), frequency="Daily")
    task2 = Task(description="Evening feed", task_time=time(18, 0), frequency="Daily")
    milo.add_task(task1)
    milo.add_task(task2)

    warnings = scheduler.get_conflict_warnings(owner)

    assert warnings == []

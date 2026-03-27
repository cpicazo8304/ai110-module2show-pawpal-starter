"""
test_pawpal.py

Unit tests for PawPal+ core scheduling behaviors.
Run with: pytest test_pawpal.py -v

"""

import pytest
from datetime import datetime, timedelta
from pawpal_system import User, Scheduler, Task, Pet, DailyPlan, Constraint


# ─────────────────────────────────────────────────────────────────────────────
# Shared helpers
# ─────────────────────────────────────────────────────────────────────────────

def make_dt(t: str, day: str = "2026-01-01") -> datetime:
    """Parse a 'HH:MM' string into a datetime on the given day."""
    return datetime.strptime(f"{day} {t}", "%Y-%m-%d %H:%M")


def make_user(slots: list[str], budget: int = 300) -> User:
    """Return a User whose available slots and time budget match the args."""
    return User(name="Tester", pets=[], time_free=budget, available=slots)


def make_constraint(slots: list[str], budget: int = 300) -> Constraint:
    return Constraint(max_time_available=budget, available_times=slots)


# ─────────────────────────────────────────────────────────────────────────────
# 1. Sorting
#
# Verifies that generate_plan() always produces a chronologically ordered
# plan regardless of the order tasks were added. Also checks that a pet
# with no tasks produces an empty plan without raising.
# ─────────────────────────────────────────────────────────────────────────────

def test_sorting():
    pet  = Pet(name="Milo", pet_type="dog")
    user = make_user(["08:00", "12:00", "18:00"])

    # Add tasks intentionally out of order
    t_feed  = Task(task_type="Feeding",      duration=15, start_time=make_dt("12:00"))
    t_play  = Task(task_type="Evening play", duration=30, start_time=make_dt("18:00"))
    t_walk  = Task(task_type="Morning walk", duration=30, start_time=make_dt("08:00"))

    scheduler = Scheduler([t_feed, t_play, t_walk], user, pet)
    plan = scheduler.generate_plan()
    times = [task.start_time for task in plan.get_tasks()]

    assert times == sorted(times), "Tasks should be sorted earliest to latest"

    # Edge case: no tasks → empty plan, no crash
    empty_scheduler = Scheduler([], user, pet)
    empty_plan = empty_scheduler.generate_plan()
    assert empty_plan.get_tasks() == [], "Empty task list should produce an empty plan"


# ─────────────────────────────────────────────────────────────────────────────
# 2. Constraint validation
#
# Confirms that is_task_allowed() correctly blocks three distinct failure modes:
#   - start time not in the user's available slots
#   - time window overlaps an already-scheduled task
#   - duration would push total scheduled time over budget
# And confirms a valid task is accepted.
# ─────────────────────────────────────────────────────────────────────────────

def test_constraint_validation():
    constraint = make_constraint(["08:00", "12:00"], budget=60)
    existing   = Task(task_type="Walk", duration=30, start_time=make_dt("08:00"))
    plan       = DailyPlan([existing], constraint)

    # Invalid slot — 09:00 not in available times
    bad_slot = Task(task_type="Bath", duration=20, start_time=make_dt("09:00"))
    assert not constraint.is_task_allowed(bad_slot, plan), \
        "Task outside available slots should be rejected"

    # Overlap — 08:15 falls inside the 08:00–08:30 walk
    overlap = Task(task_type="Groom", duration=20, start_time=make_dt("08:15"))
    overlap_constraint = make_constraint(["08:00", "08:15"], budget=300)
    overlap_plan = DailyPlan([existing], overlap_constraint)
    assert not overlap_constraint.is_task_allowed(overlap, overlap_plan), \
        "Overlapping task should be rejected"

    # Over budget — existing 30 min + 40 min > 60 min cap
    over_budget = Task(task_type="Training", duration=40, start_time=make_dt("12:00"))
    assert not constraint.is_task_allowed(over_budget, plan), \
        "Task that exceeds time budget should be rejected"

    # Happy path — valid slot, no overlap, within budget
    valid = Task(task_type="Feeding", duration=15, start_time=make_dt("12:00"))
    assert constraint.is_task_allowed(valid, plan), \
        "Valid task should be accepted"


# ─────────────────────────────────────────────────────────────────────────────
# 3. Recurring tasks
#
# Checks that mark_complete() correctly advances start_time by exactly
# one day (daily) or seven days (weekly), and that non-recurring tasks
# return None instead of a follow-up task.
# ─────────────────────────────────────────────────────────────────────────────

def test_recurring_tasks():
    base = make_dt("08:00", day="2026-01-01")

    # Daily recurrence — next task should be Jan 2 at 08:00
    daily_task = Task(task_type="Feeding", duration=15, start_time=base, frequency="daily")
    next_daily = daily_task.mark_complete()
    assert next_daily is not None, "Daily task should return a follow-up task"
    assert next_daily.start_time == base + timedelta(days=1), \
        "Daily follow-up should be scheduled exactly one day later"
    assert next_daily.completed is False, "Follow-up task should start as incomplete"

    # Weekly recurrence — next task should be Jan 8 at 08:00
    weekly_task = Task(task_type="Bath", duration=30, start_time=base, frequency="weekly")
    next_weekly = weekly_task.mark_complete()
    assert next_weekly is not None, "Weekly task should return a follow-up task"
    assert next_weekly.start_time == base + timedelta(weeks=1), \
        "Weekly follow-up should be scheduled exactly one week later"

    # Non-recurring — should return None
    one_off = Task(task_type="Vet visit", duration=60, start_time=base, frequency=None)
    result = one_off.mark_complete()
    assert result is None, "Non-recurring task should return None on completion"
    assert one_off.completed is True, "Task should be marked complete after mark_complete()"


# ─────────────────────────────────────────────────────────────────────────────
# 4. Conflict detection
#
# Validates three scenarios:
#   - Clean schedule produces zero warnings
#   - A task starting mid-window triggers exactly one warning
#   - Back-to-back tasks (end time == next start time) are NOT flagged
# ─────────────────────────────────────────────────────────────────────────────

def test_conflict_detection():
    user = make_user(["08:00", "08:15", "08:30", "12:00"])
    pet  = Pet(name="Milo", pet_type="dog")

    # No conflicts — tasks are well separated
    t1 = Task(task_type="Walk",    duration=30, start_time=make_dt("08:00"))
    t2 = Task(task_type="Feeding", duration=15, start_time=make_dt("12:00"))
    clean_plan = DailyPlan([t1, t2], make_constraint(["08:00", "12:00"]))
    scheduler  = Scheduler([t1, t2], user, pet)
    assert scheduler.detect_conflicts(clean_plan) == [], \
        "Non-overlapping tasks should produce no conflicts"

    # One conflict — 08:15 falls inside 08:00–08:30 walk
    t3 = Task(task_type="Overlap", duration=20, start_time=make_dt("08:15"))
    conflict_plan = DailyPlan([t1, t3], make_constraint(["08:00", "08:15"]))
    scheduler2    = Scheduler([t1, t3], user, pet)
    warnings = scheduler2.detect_conflicts(conflict_plan)
    assert len(warnings) == 1, "One overlapping pair should produce exactly one warning"

    # Edge case: back-to-back (08:00–08:30 then 08:30–09:00) — NOT a conflict.
    # t1 is 30 min, so it ends exactly at 08:30 when t4 starts — no overlap.
    t1_short = Task(task_type="Walk", duration=30, start_time=make_dt("08:00"))
    t4 = Task(task_type="Groom", duration=30, start_time=make_dt("08:30"))
    adjacent_plan = DailyPlan([t1_short, t4], make_constraint(["08:00", "08:30"]))
    scheduler3    = Scheduler([t1_short, t4], user, pet)
    assert scheduler3.detect_conflicts(adjacent_plan) == [], \
        "Back-to-back tasks should not be flagged as a conflict"


# ─────────────────────────────────────────────────────────────────────────────
# 5. Completion filtering
#
# Ensures filter_tasks_by_completion() returns only incomplete tasks,
# handles the all-complete edge case gracefully (empty list, no crash),
# and leaves the underlying plan unchanged.
# ─────────────────────────────────────────────────────────────────────────────

def test_completion_filtering():
    user = make_user(["08:00", "12:00", "18:00"])
    pet  = Pet(name="Milo", pet_type="dog")

    t1 = Task(task_type="Walk",    duration=30, start_time=make_dt("08:00"))
    t2 = Task(task_type="Feeding", duration=15, start_time=make_dt("12:00"))
    t3 = Task(task_type="Play",    duration=20, start_time=make_dt("18:00"))

    scheduler = Scheduler([t1, t2, t3], user, pet)
    plan      = scheduler.generate_plan()

    # Mark one task complete
    t1.completed = True
    incomplete = scheduler.filter_tasks_by_completion(plan)
    assert len(incomplete) == 2, "Filter should return two incomplete tasks"
    assert t1 not in incomplete, "Completed task should not appear in filtered list"

    # Underlying plan should be unmodified
    assert len(plan.get_tasks()) == 3, "Filter should not mutate the original plan"

    # Edge case: all tasks complete → empty list, no crash
    t2.completed = True
    t3.completed = True
    all_done = scheduler.filter_tasks_by_completion(plan)
    assert all_done == [], "All tasks complete should return an empty list"
from pawpal_system import User, Scheduler, Task, Pet, DailyPlan, Constraint
from datetime import datetime

# ─────────────────────────────────────────────
# Shared setup
# ─────────────────────────────────────────────
def make_dt(t: str) -> datetime:
    return datetime.strptime(f"2026-01-01 {t}", "%Y-%m-%d %H:%M")

def section(title: str):
    print(f"\n{'='*50}")
    print(f"  {title}")
    print('='*50)

pet = Pet(name="Milo", pet_type="dog", age=3)
user = User(
    name="Cesar",
    pets=[pet],
    time_free=240,
    available=["08:00", "09:00", "12:00", "13:00", "15:00", "18:00"],
)


# ─────────────────────────────────────────────
# SORTING TEST
# Tasks added out of order: 12:00, 18:00, 08:00
# Expected output: sorted 08:00 → 12:00 → 18:00
# ─────────────────────────────────────────────
section("SORTING TEST")

task_feed   = Task(task_type="Feeding",       duration=15, start_time=make_dt("12:00"))
task_play   = Task(task_type="Evening play",  duration=45, start_time=make_dt("18:00"))
task_walk   = Task(task_type="Morning walk",  duration=30, start_time=make_dt("08:00"))

scheduler = Scheduler([task_feed, task_play, task_walk], user, pet)
plan = scheduler.generate_plan()

print("Tasks added in order: Feeding (12:00), Evening play (18:00), Morning walk (08:00)")
print("Expected sorted order: Morning walk → Feeding → Evening play\n")
for task in plan.get_tasks():
    print(f"  {task.start_time.strftime('%H:%M')}  {task.task_type}")

# Note: You can see that when scheduler generates the plan, it sorts the tasks by their start time. 
# The output should show the tasks in chronological order based on their start times, 
# regardless of the order they were added to the scheduler.


# ─────────────────────────────────────────────
# FILTERING TEST
# Mark one task complete, filter should hide it
# Expected: only incomplete tasks remain
# ─────────────────────────────────────────────
section("FILTERING TEST")

task_walk2  = Task(task_type="Morning walk",  duration=30, start_time=make_dt("08:00"))
task_feed2  = Task(task_type="Feeding",       duration=15, start_time=make_dt("12:00"))
task_play2  = Task(task_type="Evening play",  duration=45, start_time=make_dt("18:00"))

scheduler2 = Scheduler([task_walk2, task_feed2, task_play2], user, pet)
plan2 = scheduler2.generate_plan()

print("Before filtering (all tasks):")
for t in plan2.get_tasks():
    status = "✅" if t.completed else "❌"
    print(f"  {status}  {t.task_type}")

task_walk2.mark_complete()  # mark Morning walk as done

print("\nAfter marking 'Morning walk' complete — filtering incomplete only:")
incomplete = scheduler2.filter_tasks_by_completion(plan2)
if incomplete:
    for t in incomplete:
        print(f"  ❌  {t.task_type}")
else:
    print("  All tasks completed!")

print("\nEdge case — mark ALL tasks complete:")
task_feed2.mark_complete()
task_play2.mark_complete()
all_done = scheduler2.filter_tasks_by_completion(plan2)
print(f"  Remaining tasks: {len(all_done)} (expected 0)")

# Note: The filtering test demonstrates how marking a task as complete affects the 
# list of tasks returned by the filter.


# ─────────────────────────────────────────────
# CONFLICT DETECTION TEST
# Case 1: no conflicts
# Case 2: one overlap (08:15 start overlaps 08:00–08:30 walk)
# Case 3: multiple overlaps
# ─────────────────────────────────────────────
section("CONFLICT DETECTION TEST")

# Case 1 — clean schedule, no conflicts
print("Case 1: no conflicts expected")
task_a = Task(task_type="Morning walk", duration=30, start_time=make_dt("08:00"))
task_b = Task(task_type="Feeding",      duration=15, start_time=make_dt("12:00"))
scheduler3 = Scheduler([task_a, task_b], user, pet)
plan3 = scheduler3.generate_plan()
conflicts = scheduler3.detect_conflicts(plan3)
print(f"  Conflicts found: {len(conflicts)} (expected 0)")

# Case 2 — one conflict: 08:15 start overlaps 08:00–08:30 walk
print("\nCase 2: one conflict expected (08:15 overlaps 08:00–08:30 walk)")
task_c = Task(task_type="Morning walk",    duration=30, start_time=make_dt("08:00"))
task_d = Task(task_type="Overlapping task", duration=20, start_time=make_dt("08:15"))

# bypass constraint (08:15 not in available slots) to test detect_conflicts directly
plan4 = DailyPlan([task_c, task_d], Constraint(
    max_time_available=240,
    available_times=["08:00", "08:15", "12:00"],
))
scheduler4 = Scheduler([task_c, task_d], user, pet)
conflicts2 = scheduler4.detect_conflicts(plan4)
print(f"  Conflicts found: {len(conflicts2)} (expected 1)")
for w in conflicts2:
    print(f"  {w}")

# Case 3 — two conflicts: 08:15 overlaps walk, 09:10 overlaps a 09:00 task
print("\nCase 3: two conflicts expected")
task_e = Task(task_type="Morning walk",  duration=30, start_time=make_dt("08:00"))
task_f = Task(task_type="Overlap A",     duration=20, start_time=make_dt("08:15"))
task_g = Task(task_type="Bath",          duration=30, start_time=make_dt("09:00"))
task_h = Task(task_type="Overlap B",     duration=20, start_time=make_dt("09:10"))  # not in slots
plan5 = DailyPlan([task_e, task_f, task_g, task_h], Constraint(
    max_time_available=240,
    available_times=["08:00", "08:15", "09:00", "09:10", "12:00"],
))
scheduler5 = Scheduler([task_e, task_f, task_g, task_h], user, pet)
conflicts3 = scheduler5.detect_conflicts(plan5)
print(f"  Conflicts found: {len(conflicts3)} (expected 2)")
for w in conflicts3:
    print(f"  {w}")
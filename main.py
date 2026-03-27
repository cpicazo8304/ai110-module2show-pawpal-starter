from pawpal_system import User, Scheduler, Task, Pet, DailyPlan, Constraint
from datetime import datetime, timedelta, date, time

if __name__ == '__main__':    
    pet1 = Pet(name="Milo", pet_type="dog", age=3)
    pet2 = Pet(name="Sammy", pet_type="dog", age=3)
    task1 = Task(task_type="Morning walk", duration=30, start_time=datetime.strptime("2026-01-01 08:00", "%Y-%m-%d %H:%M"))
    task2 = Task(task_type="Feeding", duration=15, start_time=datetime.strptime("2026-01-01 12:00", "%Y-%m-%d %H:%M"))
    task3 = Task(task_type="Evening play", duration=45, start_time=datetime.strptime("2026-01-01 18:00", "%Y-%m-%d %H:%M"))
    user = User(name="Cesar", pets=[pet1, pet2], time_free=120, available=["08:00", "12:00", "18:00"])

    # Print Today's Schedule
    scheduler1 = Scheduler([task1, task2, task3], user, pet1)
    plan = scheduler1.generate_plan()

    scheduler2 = Scheduler([task1, task2, task3], user, pet2)
    plan2 = scheduler2.generate_plan()

    print(scheduler1.explain_plan(plan))
    print()
    print(scheduler2.explain_plan(plan2))

    # Update your main.py to add tasks out of order, 
    # then print the results using your new sorting and 
    # filtering methods to ensure they work in the terminal.
    
    # sorting test cases
    task4 = Task(task_type="Afternoon walk", duration=30, start_time=datetime.strptime("2026-01-01 15:00", "%Y-%m-%d %H:%M"))
    scheduler1.tasks.append(task4)
    print()
    print(scheduler1.explain_plan(plan))
    plan = scheduler1.generate_plan()  # sorts new additions
    print()
    print(scheduler1.explain_plan(plan))
    print()

    # filtering test cases
    print("\nBefore marking task as completed:")
    print()
    print(scheduler1.explain_plan(plan))
    print()
    task1.completed = True

    filtered_tasks = scheduler1.filter_tasks_by_completion(plan)

    print("\nAfter marking task as completed:")
    print()
    new_plan = DailyPlan(filtered_tasks, scheduler1.constraints)
    print(scheduler1.explain_plan(new_plan))
    print()

    # detecting conflicts test cases
    task5 = Task(task_type="Conflicting task", duration=30, start_time=datetime.strptime("2026-01-01 08:15", "%Y-%m-%d %H:%M"))
    scheduler1.tasks.append(task5)
    plan = scheduler1.generate_plan()
    conflicts = scheduler1.detect_conflicts(plan)
    print("\nConflicts detected:")
    for warning in conflicts:
        print(warning)
    
from pawpal_system import User, Scheduler, Task, Pet


if __name__ == '__main__':    
    pet1 = Pet(name="Milo", pet_type="dog", age=3)
    pet2 = Pet(name="Sammy", pet_type="dog", age=3)
    task1 = Task(task_type="Morning walk", duration=30, start_time="08:00")
    task2 = Task(task_type="Feeding", duration=15, start_time="12:00")
    task3 = Task(task_type="Evening play", duration=45, start_time="18:00")
    user = User(name="Cesar", pets=[pet1, pet2], time_free=120, available=["08:00", "12:00", "18:00"])

    # Print Today's Schedule
    scheduler1 = Scheduler([task1, task2, task3], user, pet1)
    plan = scheduler1.generate_plan()

    scheduler2 = Scheduler([task1, task2, task3], user, pet2)
    plan2 = scheduler2.generate_plan()

    print(scheduler1.explain_plan(plan))
    print()
    print(scheduler2.explain_plan(plan2))
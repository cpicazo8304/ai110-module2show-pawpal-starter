# test_pawpal.py
import pytest
from datetime import datetime
from pawpal_system import Task, Pet, Scheduler, User  # adjust import if needed

def test_task_completion():
    task = Task("Walk dog", 30, "08:00")
    assert not task.completed  # initially False
    task.mark_complete()
    assert task.completed  # should now be True

def test_task_addition():
    pet = Pet("Fido", "Dog")
    user = User("Alice", [pet], time_free=120, available=["08:00", "12:00", "18:00"])
    assert pet.get_task_count() == 0
    new_task = Task("Feed dog", 10, "08:00")
    scheduler = Scheduler(tasks=[new_task], user=user, pet=pet)
    scheduler.generate_plan()
    assert pet.get_task_count() == 1


if __name__ == "__main__":
    pytest.main()
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime, timedelta, date

from streamlit import user


@dataclass
class Pet:
    name: str
    pet_type: str
    age: Optional[int] = None
    task_count: int = 0

    def update_task_count(self):
        """Update the task count for this pet."""
        self.task_count += 1

    def get_info(self) -> str:
        """Return a string with pet information."""
        age_str = f", Age: {self.age}" if self.age else ""
        return f"Name: {self.name}, Type: {self.pet_type}{age_str}"
    
    def get_task_count(self) -> int:
        """Return the number of tasks assigned to this pet."""
        return self.task_count


@dataclass
class Task:
    task_type: str
    duration: int  # in minutes
    start_time: Optional[str] = None  # in HH:MM format
    completed: bool = False  # new attribute

    def mark_complete(self):
        """Mark this task as completed."""
        self.completed = True

    def set_start_time(self, start_time: str):
        """Set the task's start time with validation."""
        try:
            dt = datetime.strptime(start_time, "%H:%M")
            self.start_time = dt.strftime("%H:%M")
        except ValueError:
            raise ValueError(f"Invalid time format: {start_time}. Use HH:MM 24-hour format.")

    def update_duration(self, new_duration: int):
        """Update the task's duration."""
        self.duration = new_duration

    def get_start_time(self):
        """Return the start time of the task."""
        return self.start_time

    def get_end_time(self):
        """Calculate and return the end time of the task."""
        if self.start_time is None:
            return None
        # Use today as reference date
        today = date.today()
        start_dt = datetime.strptime(self.start_time, "%H:%M").replace(
            year=today.year, month=today.month, day=today.day
        )
        end_dt = start_dt + timedelta(minutes=self.duration)
        return end_dt.strftime("%H:%M")
    
    def get_duration(self) -> int:
        """Return the duration of the task."""
        return self.duration

@dataclass
class User:
    name: str
    pets: List[Pet]
    time_free: int
    available: List[str]

    def update_time_free(self, new_time_free: int):
        """Update the user's free time."""
        self.time_free = new_time_free

    def update_available_times(self, new_available_times: List[str]):
        """Update the user's available times."""
        self.available = new_available_times

    def update_pets(self, new_pets: List[Pet]):
        """Update the user's pets."""
        self.pets = new_pets

    def get_time_free(self) -> int:
        """Return the user's free time."""
        return self.time_free

    def get_available_times(self) -> List[str]:
        """Return the user's available times."""
        return self.available

    def get_pets(self) -> List[Pet]:
        """Return the user's pets."""
        return self.pets


class Constraint:
    def __init__(self, max_time_available: int, available_times: List[str]):
        self.max_time_available = max_time_available
        self.available_times = []
        for time_str in available_times:
            try:
                dt = datetime.strptime(time_str, "%H:%M")
                self.available_times.append(dt.strftime("%H:%M"))
            except ValueError:
                raise ValueError(f"Invalid available time: {time_str}. Use HH:MM 24-hour format.")

    def is_task_allowed(self, task: Task, current_plan: 'DailyPlan') -> bool:
        """Check if a task is allowed given the current plan."""
        if task.get_start_time() not in self.available_times:
            return False
        
        # Check for time overlap with existing tasks
        for existing_task in current_plan.task_list:
            if existing_task.start_time and task.start_time:
                existing_end_str = existing_task.get_end_time()
                new_end_str = task.get_end_time()
                if existing_end_str and new_end_str:
                    existing_start = datetime.strptime(existing_task.start_time, "%H:%M")
                    existing_end = datetime.strptime(existing_end_str, "%H:%M")
                    new_start = datetime.strptime(task.start_time, "%H:%M")
                    new_end = datetime.strptime(new_end_str, "%H:%M")
                    if new_start < existing_end and new_end > existing_start:
                        return False
        
        if current_plan.get_total_time() + task.get_duration() > self.max_time_available:
            return False
        return True

    def apply(self, plan: 'DailyPlan'):
        """Apply the constraint to the plan."""
        new_task_list = []
        temp_plan = DailyPlan([], plan.constraints)
        for task in plan.task_list:
            if self.is_task_allowed(task, temp_plan):
                temp_plan.add_task(task)
                new_task_list.append(task)
        plan.task_list = new_task_list
        plan.total_time = plan.get_total_time()


class DailyPlan:
    def __init__(self, task_list: List[Task], constraints: Constraint):
        self.task_list = task_list
        self.total_time = sum(task.get_duration() for task in task_list)
        self.constraints = constraints

    def add_task(self, task: Task, pet: Optional[Pet] = None):
        """Add a task to the plan."""
        if self.constraints.is_task_allowed(task, self):
            self.task_list.append(task)
            duration = task.duration
            self.total_time += duration
            if pet:
                pet.update_task_count()

    def remove_task(self, task: Task):
        """Remove a task from the plan."""
        if task in self.task_list:
            duration = task.duration
            self.task_list.remove(task)
            self.total_time -= duration

    def edit_task(self, task: Task):
        """Edit an existing task in the plan."""
        pass

    def get_total_time(self) -> int:
        """Calculate and return the total time for all tasks."""
        return self.total_time

    def get_tasks(self) -> List[Task]:
        """Return the list of tasks in the plan."""
        return self.task_list


class Scheduler:
    def __init__(self, tasks: List[Task], user: User, pet: Pet):
        self.tasks = tasks
        self.user = user
        self.constraints = Constraint(max_time_available=self.user.get_time_free(), available_times=self.user.get_available_times())
        self.pet = pet

    def generate_plan(self) -> DailyPlan:
        """Generate a daily plan based on tasks and constraints."""
        sorted_tasks = self.sort_tasks_by_priority()
        plan = DailyPlan([], self.constraints)
        for task in sorted_tasks:
            plan.add_task(task, self.pet)
        return plan

    def sort_tasks_by_priority(self) -> List[Task]:
        """Sort tasks by start_time (newest first). Tasks without start_time go last."""
        return sorted(
            self.tasks,
            key=lambda t: datetime.strptime(t.start_time, "%H:%M") if t.start_time else datetime.min,
            reverse=False
        )
    
    def apply_constraints(self, plan: DailyPlan):
        """Apply constraints to the plan."""
        self.constraints.apply(plan)

    def explain_plan(self, plan: DailyPlan) -> str:
        """Provide an explanation for the generated plan."""
        tasks = plan.get_tasks()
        if not tasks:
            return "No tasks in the plan."
        explanation = f"The pet {self.pet.name} has the following tasks scheduled:\n"
        for task in tasks:
            start_str = f" (start at {task.start_time})" if task.start_time else ""
            explanation += f"- {task.task_type}: {task.duration} minutes{start_str}\n"
        explanation += f"Total time: {plan.get_total_time()} minutes"
        return explanation
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Pet:
    name: str
    pet_type: str
    age: Optional[int] = None

    def get_info(self) -> str:
        """Return a string with pet information."""
        pass


@dataclass
class Task:
    task_type: str
    duration: int  # in minutes
    priority: int  # e.g., 1-5
    preferred_time: str  # e.g., 'morning', 'afternoon'

    def update_priority(self, new_priority: int):
        """Update the task's priority."""
        pass

    def update_duration(self, new_duration: int):
        """Update the task's duration."""
        pass

@dataclass
@dataclass
class User:
    name: str
    pet: Pet
    preferences: List[str]

    def update_preferences(self, new_preferences: List[str]):
        """Update user preferences."""
        self.preferences = new_preferences

    def get_pet(self) -> Pet:
        """Return the user's pet."""
        return self.pet


class Constraint:
    def __init__(self, max_time_available: int, preferred_times: List[str], priority_rules: Optional[dict] = None):
        self.max_time_available = max_time_available
        self.preferred_times = preferred_times
        self.priority_rules = priority_rules

    def is_task_allowed(self, task: Task, current_plan: 'DailyPlan') -> bool:
        """Check if a task is allowed given the current plan."""
        pass

    def check_time_constraint(self, plan: 'DailyPlan') -> bool:
        """Check if the plan meets time constraints."""
        pass

    def apply(self, plan: 'DailyPlan'):
        """Apply the constraint to the plan."""
        pass


class DailyPlan:
    def __init__(self, task_list: List[Task], total_time: int, constraints: List[Constraint]):
        self.task_list = task_list
        self.total_time = total_time
        self.constraints = constraints

    def add_task(self, task: Task):
        """Add a task to the plan."""
        pass

    def remove_task(self, task: Task):
        """Remove a task from the plan."""
        pass

    def edit_task(self, task: Task):
        """Edit an existing task in the plan."""
        pass

    def calculate_total_time(self) -> int:
        """Calculate and return the total time for all tasks."""
        pass

    def get_tasks(self) -> List[Task]:
        """Return the list of tasks in the plan."""
        pass


class Scheduler:
    def __init__(self, tasks: List[Task], constraints: List[Constraint]):
        self.tasks = tasks
        self.constraints = constraints

    def generate_plan(self) -> DailyPlan:
        """Generate a daily plan based on tasks and constraints."""
        pass

    def sort_tasks_by_priority(self) -> List[Task]:
        """Sort tasks by priority."""
        pass

    def apply_constraints(self, plan: DailyPlan):
        """Apply constraints to the plan."""
        pass

    def explain_plan(self, plan: DailyPlan) -> str:
        """Provide an explanation for the generated plan."""
        pass
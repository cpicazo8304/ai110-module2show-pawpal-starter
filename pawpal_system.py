"""
pet_scheduler.py

A scheduling system for managing daily pet care tasks.
Defines data models for pets, tasks, and users, along with constraint
validation and plan generation logic via a Scheduler.
"""

from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime, timedelta, date

from streamlit import user


@dataclass
class Pet:
    """
    Represents a pet with basic identifying information and a task counter.

    Attributes:
        name (str): The pet's name.
        pet_type (str): The type/species of the pet (e.g., 'dog', 'cat').
        age (Optional[int]): The pet's age in years. Defaults to None if unknown.
        task_count (int): Running total of tasks assigned to this pet. Defaults to 0.
    """

    name: str
    pet_type: str
    age: Optional[int] = None
    task_count: int = 0

    def update_task_count(self):
        """Increment the pet's task count by 1."""
        self.task_count += 1

    def get_info(self) -> str:
        """
        Build a human-readable summary of the pet's information.

        Returns:
            str: A formatted string with name, type, and optionally age.
        """
        age_str = f", Age: {self.age}" if self.age else ""
        return f"Name: {self.name}, Type: {self.pet_type}{age_str}"
    
    def get_task_count(self) -> int:
        """
        Return the total number of tasks assigned to this pet.

        Returns:
            int: The current task count.
        """
        return self.task_count


@dataclass
class Task:
    """
    Represents a single schedulable pet care task.

    Attributes:
        task_type (str): The category/name of the task (e.g., 'walk', 'feeding').
        duration (int): How long the task takes, in minutes.
        start_time (Optional[str]): The scheduled start time in 'HH:MM' 24-hour format.
                                    Defaults to None if unscheduled.
        completed (bool): Whether the task has been completed. Defaults to False.
    """

    task_type: str
    duration: int  # in minutes
    start_time: Optional[str] = None  # in HH:MM format
    completed: bool = False  # new attribute

    def mark_complete(self):
        """Mark this task as completed by setting the completed flag to True."""
        self.completed = True

    def set_start_time(self, start_time: str):
        """
        Set and validate the task's start time.

        Args:
            start_time (str): Time string in 'HH:MM' 24-hour format.

        Raises:
            ValueError: If the provided string does not match the expected format.
        """
        try:
            dt = datetime.strptime(start_time, "%H:%M")
            self.start_time = dt.strftime("%H:%M")
        except ValueError:
            raise ValueError(f"Invalid time format: {start_time}. Use HH:MM 24-hour format.")

    def update_duration(self, new_duration: int):
        """
        Replace the task's duration with a new value.

        Args:
            new_duration (int): The updated duration in minutes.
        """
        self.duration = new_duration

    def get_start_time(self):
        """
        Return the task's scheduled start time.

        Returns:
            Optional[str]: The start time in 'HH:MM' format, or None if not set.
        """
        return self.start_time

    def get_end_time(self):
        """
        Calculate the task's end time based on its start time and duration.

        Uses today's date as a reference to perform the arithmetic, handling
        potential midnight rollovers correctly.

        Returns:
            Optional[str]: The calculated end time in 'HH:MM' format,
                           or None if start_time is not set.
        """
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
        """
        Return the duration of the task.

        Returns:
            int: Task duration in minutes.
        """
        return self.duration


@dataclass
class User:
    """
    Represents the pet owner with scheduling availability information.

    Attributes:
        name (str): The owner's name.
        pets (List[Pet]): The pets owned by this user.
        time_free (int): Total free time available today, in minutes.
        available (List[str]): List of available start times in 'HH:MM' format.
    """

    name: str
    pets: List[Pet]
    time_free: int
    available: List[str]

    def update_time_free(self, new_time_free: int):
        """
        Update the user's total available free time.

        Args:
            new_time_free (int): New free time value in minutes.
        """
        self.time_free = new_time_free

    def update_available_times(self, new_available_times: List[str]):
        """
        Replace the user's list of available time slots.

        Args:
            new_available_times (List[str]): New list of times in 'HH:MM' format.
        """
        self.available = new_available_times

    def update_pets(self, new_pets: List[Pet]):
        """
        Replace the user's list of pets.

        Args:
            new_pets (List[Pet]): Updated list of Pet objects.
        """
        self.pets = new_pets

    def get_time_free(self) -> int:
        """
        Return the user's total free time.

        Returns:
            int: Free time in minutes.
        """
        return self.time_free

    def get_available_times(self) -> List[str]:
        """
        Return the user's available time slots.

        Returns:
            List[str]: Available start times in 'HH:MM' format.
        """
        return self.available

    def get_pets(self) -> List[Pet]:
        """
        Return the user's list of pets.

        Returns:
            List[Pet]: The pets associated with this user.
        """
        return self.pets


class Constraint:
    """
    Encapsulates scheduling rules that restrict which tasks may be added to a plan.

    Validates that tasks start at permitted times, do not overlap with already-
    scheduled tasks, and do not exceed the user's total available time budget.

    Attributes:
        max_time_available (int): Maximum total minutes that can be scheduled.
        available_times (List[str]): Permitted task start times in 'HH:MM' format.
    """

    def __init__(self, max_time_available: int, available_times: List[str]):
        """
        Initialize a Constraint, validating and normalizing available times.

        Args:
            max_time_available (int): Upper bound on total scheduled minutes.
            available_times (List[str]): Allowed start times; must be in 'HH:MM' format.

        Raises:
            ValueError: If any time string in available_times is not valid 'HH:MM'.
        """
        self.max_time_available = max_time_available
        self.available_times = []
        for time_str in available_times:
            try:
                dt = datetime.strptime(time_str, "%H:%M")
                self.available_times.append(dt.strftime("%H:%M"))
            except ValueError:
                raise ValueError(f"Invalid available time: {time_str}. Use HH:MM 24-hour format.")

    def is_task_allowed(self, task: Task, current_plan: 'DailyPlan') -> bool:
        """
        Determine whether a task can legally be added to the current plan.

        Three checks are performed in order:
          1. The task's start time must be in the list of permitted times.
          2. The task must not time-overlap with any already-scheduled task.
          3. Adding the task must not push total scheduled time over the budget.

        Args:
            task (Task): The task being evaluated.
            current_plan (DailyPlan): The plan the task would be added to.

        Returns:
            bool: True if the task passes all constraint checks, False otherwise.
        """
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
        """
        Filter an existing plan's task list to only retain constraint-compliant tasks.

        Iterates over the plan's tasks, rebuilding a clean temporary plan to perform
        accurate cumulative time checks, then replaces the plan's task list in-place.

        Args:
            plan (DailyPlan): The plan to be filtered and updated.
        """
        new_task_list = []
        temp_plan = DailyPlan([], plan.constraints)
        for task in plan.task_list:
            if self.is_task_allowed(task, temp_plan):
                temp_plan.add_task(task)
                new_task_list.append(task)
        plan.task_list = new_task_list
        plan.total_time = plan.get_total_time()


class DailyPlan:
    """
    Represents a single day's scheduled pet care tasks.

    Manages a list of Task objects and enforces constraint checks on every
    addition. Tracks total scheduled time as tasks are added or removed.

    Attributes:
        task_list (List[Task]): The ordered list of tasks in this plan.
        total_time (int): Cumulative duration of all tasks in minutes.
        constraints (Constraint): The rules governing what may be scheduled.
    """

    def __init__(self, task_list: List[Task], constraints: Constraint):
        """
        Initialize a DailyPlan and compute initial total time from the task list.

        Args:
            task_list (List[Task]): Pre-existing tasks to seed the plan with.
            constraints (Constraint): Constraint object used to validate tasks.
        """
        self.task_list = task_list
        self.total_time = sum(task.get_duration() for task in task_list)
        self.constraints = constraints

    def add_task(self, task: Task, pet: Optional[Pet] = None):
        """
        Attempt to add a task to the plan if it satisfies all constraints.

        If a Pet is provided, its task counter is incremented on successful addition.

        Args:
            task (Task): The task to add.
            pet (Optional[Pet]): The pet the task is for; used to update task count.
        """
        if self.constraints.is_task_allowed(task, self):
            self.task_list.append(task)
            duration = task.duration
            self.total_time += duration
            if pet:
                pet.update_task_count()

    def remove_task(self, task: Task):
        """
        Remove a task from the plan and subtract its duration from the total.

        Does nothing if the task is not currently in the plan.

        Args:
            task (Task): The task to remove.
        """
        if task in self.task_list:
            duration = task.duration
            self.task_list.remove(task)
            self.total_time -= duration

    def edit_task(self, task: Task):
        """
        Edit an existing task in the plan.

        Args:
            task (Task): The task with updated values.

        Note:
            Not yet implemented.
        """
        pass

    def get_total_time(self) -> int:
        """
        Return the cumulative duration of all tasks currently in the plan.

        Returns:
            int: Total scheduled time in minutes.
        """
        return self.total_time

    def get_tasks(self) -> List[Task]:
        """
        Return the list of tasks currently in the plan.

        Returns:
            List[Task]: All scheduled tasks.
        """
        return self.task_list


class Scheduler:
    """
    Orchestrates the creation of a DailyPlan for a specific pet and user.

    Builds a Constraint from the user's availability, sorts tasks by start time,
    and adds them to a plan in chronological order.

    Attributes:
        tasks (List[Task]): All candidate tasks to be scheduled.
        user (User): The owner whose availability governs scheduling.
        constraints (Constraint): Derived from the user's free time and available slots.
        pet (Pet): The pet the schedule is being built for.
    """

    def __init__(self, tasks: List[Task], user: User, pet: Pet):
        """
        Initialize the Scheduler for a given user and pet.

        Args:
            tasks (List[Task]): Candidate tasks to schedule.
            user (User): The pet owner providing availability constraints.
            pet (Pet): The pet receiving the scheduled care.
        """
        self.tasks = tasks
        self.user = user
        self.constraints = Constraint(max_time_available=self.user.get_time_free(), available_times=self.user.get_available_times())
        self.pet = pet

    def generate_plan(self) -> DailyPlan:
        """
        Produce a constraint-validated DailyPlan from the available tasks.

        Tasks are sorted chronologically before being added so that earlier
        start times take priority when the time budget is limited.

        Returns:
            DailyPlan: The finalized plan containing all schedulable tasks.
        """
        sorted_tasks = self.sort_tasks_by_priority()
        plan = DailyPlan([], self.constraints)
        for task in sorted_tasks:
            plan.add_task(task, self.pet)
        return plan

    def sort_tasks_by_priority(self) -> List[Task]:
        """
        Sort the task list in ascending chronological order by start time.

        Tasks without a start time are placed at the end of the list, as
        datetime.min is used as their sort key.

        Returns:
            List[Task]: Tasks ordered from earliest to latest start time.
        """
        return sorted(
            self.tasks,
            key=lambda t: datetime.strptime(t.start_time, "%H:%M") if t.start_time else datetime.min,
            reverse=False
        )
    
    def apply_constraints(self, plan: DailyPlan):
        """
        Apply this scheduler's constraints to an existing plan, removing invalid tasks.

        Args:
            plan (DailyPlan): The plan to be filtered in-place.
        """
        self.constraints.apply(plan)

    def explain_plan(self, plan: DailyPlan) -> str:
        """
        Generate a human-readable summary of all tasks in the plan.

        Lists each task's type, duration, and start time (if available),
        followed by the total scheduled time.

        Args:
            plan (DailyPlan): The plan to summarize.

        Returns:
            str: A formatted multi-line explanation of the plan.
        """
        tasks = plan.get_tasks()
        if not tasks:
            return "No tasks in the plan."
        explanation = f"The pet {self.pet.name} has the following tasks scheduled:\n"
        for task in tasks:
            start_str = f" (start at {task.start_time})" if task.start_time else ""
            explanation += f"- {task.task_type}: {task.duration} minutes{start_str}\n"
        explanation += f"Total time: {plan.get_total_time()} minutes"
        return explanation
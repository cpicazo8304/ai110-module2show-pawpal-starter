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
        start_time (Optional[time]): The scheduled start time as a datetime.time object.
                                     Defaults to None if unscheduled.
        completed (bool): Whether the task has been completed. Defaults to False.
    """

    task_type: str
    duration: int
    start_time: datetime
    completed: bool = False
    frequency: Optional[str] = None

    def mark_complete(self) -> Optional['Task']:
        """Mark this task as completed by setting the completed flag to True."""
        self.completed = True

        if self.frequency == "daily":
            return Task(
                task_type=self.task_type,
                duration=self.duration,
                start_time=self.start_time + timedelta(days=1),
                frequency=self.frequency,
            )
        elif self.frequency == "weekly":
            return Task(
                task_type=self.task_type,
                duration=self.duration,
                start_time=self.start_time + timedelta(weeks=1),
                frequency=self.frequency,
            )
        return None

    def set_start_time(self, start_time: str):
        """
        Set and validate the task's start time.

        Converts a string in 'HH:MM' format into a datetime.time object
        for consistent internal representation.

        Args:
            start_time (str): Time string in 'HH:MM' 24-hour format.

        Raises:
            ValueError: If the provided string does not match the expected format.
        """
        try:
            self.start_time = datetime.strptime(start_time, "%Y-%m-%d %H:%M")
        except ValueError:
            raise ValueError(
                f"Invalid datetime format: {start_time}. Use YYYY-MM-DD HH:MM."
            )

    def update_duration(self, new_duration: int): 
        """ 
        Replace the task's duration with a new value. 
        Args: new_duration (int): The updated duration in 
        minutes. 
        """ 
        self.duration = new_duration

    def get_start_time(self) -> datetime:
        """
        Return the task's scheduled start time.

        Returns:
            Optional[datetime]: The start time as a datetime object,
                            or None if not set.
        """
        return self.start_time

    def get_end_time(self) -> datetime:
        """
        Calculate the task's end time based on its start time and duration.

        Uses today's date as a reference to safely perform time arithmetic,
        then returns only the time portion.

        Returns:
            Optional[datetime]: The calculated end time as a datetime object,
                            or None if start_time is not set.
        """
        start_dt = self.start_time
        end_dt = start_dt + timedelta(minutes=self.duration) 
        return end_dt
    
    def get_duration(self) -> int: 
        """ 
        Return the duration of the task. Returns: int: Task duration in minutes. 
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
        from datetime import time as time_type
        self._available_time_slots: List[time_type] = []
        for time_str in available_times:
            try:
                self._available_time_slots.append(
                    datetime.strptime(time_str, "%H:%M").time()
                )
            except ValueError:
                raise ValueError(f"Invalid time: {time_str}")

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
        # Slot check: only the clock time matters for available_times
        if task.start_time.time() not in self._available_time_slots:
            return False

        # Overlap check: start_time is already datetime, compare directly
        for existing in current_plan.task_list:
            if existing.start_time and task.start_time:
                if task.start_time < existing.get_end_time() and \
                   task.get_end_time() > existing.start_time:
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
        sorted_tasks = self.sort_tasks_by_time()
        plan = DailyPlan([], self.constraints)
        for task in sorted_tasks:
            plan.add_task(task, self.pet)
        return plan

    def sort_tasks_by_time(self) -> List[Task]:
        """
        Sort the task list in ascending chronological order by start time.

        Tasks are compared by converting their time values into full datetime
        objects (using today's date). Tasks without a start time are placed
        at the end using datetime.min.

        Returns:
            List[Task]: Tasks ordered from earliest to latest start time.
        """
        return sorted(
            self.tasks,
            key=lambda t: t.start_time if t.start_time else datetime.min,
        )
    
    def filter_tasks_by_completion(self, plan: DailyPlan) -> List[Task]:
        """
        Filter the plan's tasks to only include those that are not marked as completed.

        Args:
            plan (DailyPlan): The plan whose tasks are to be filtered.
        """
        return [task for task in plan.get_tasks() if not task.completed]
    
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
            start_str = (
                f" (start at {task.start_time.strftime('%Y-%m-%d %H:%M')})"
                if task.start_time else ""
            )
            explanation += f"- {task.task_type}: {task.duration} minutes{start_str}\n"
        explanation += f"Total time: {plan.get_total_time()} minutes"
        return explanation

    def detect_conflicts(self, plan: DailyPlan) -> List[str]:
        """
        Check all task pairs in the plan for time overlaps.

        Uses a lightweight O(n²) pairwise comparison: for every unique
        pair of tasks, convert their start/end to datetime objects and
        test whether the intervals overlap. Returns human-readable warning
        strings — one per conflict — rather than raising an exception.

        Returns:
            List[str]: A (possibly empty) list of conflict warning messages.
        """
        warnings = []
        tasks = plan.get_tasks()
        for i in range(len(tasks)):
            for j in range(i + 1, len(tasks)):
                a, b = tasks[i], tasks[j]
                if not (a.start_time and b.start_time):
                    continue
                if a.start_time < b.get_end_time() and a.get_end_time() > b.start_time:
                    warnings.append(
                        f"⚠️ Conflict: '{a.task_type}' "
                        f"({a.start_time.strftime('%Y-%m-%d %H:%M')}–"
                        f"{a.get_end_time().strftime('%H:%M')}) "
                        f"overlaps with '{b.task_type}' "
                        f"({b.start_time.strftime('%Y-%m-%d %H:%M')}–"
                        f"{b.get_end_time().strftime('%H:%M')})"
                    )
        return warnings

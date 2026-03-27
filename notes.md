# Three main actions a user could do: 

-A user could add their and their pet's info.
-A user could add events that have different time lengths and priorities.
-A user could see a visualization of their plan.


# PawPal+ Object Design

## User Class
Represents the pet owner.

### Attributes:
- name
- pet (Pet)
- preferences (dict or list)  

### Methods:
- update_preferences()
- get_pet()


## Pet Class
Represents the pet being cared for.

### Attributes:
- name
- pet_type  # dog, cat, etc.
- age (optional)

### Methods:
- get_info()


## Task Class
Represents a single care task.

### Attributes:
- task_type  # walk, feed, meds, etc.
- duration  # in minutes
- priority  # e.g., 1–5 or low/medium/high
- preferred_time  # morning, afternoon, etc.

### Methods:
- update_priority()
- update_duration()


## DailyPlan Class
Represents the plan for one day.

### Attributes:
- task_list (list of Task)
- total_time
- constraints (list of Constraint)

### Methods:
- add_task(task)
- remove_task(task)
- edit_task(task)
- calculate_total_time()
- get_tasks()


## Scheduler Class
Responsible for generating a valid daily plan.

### Attributes:
- tasks (list of Task)
- constraints (list of Constraint)

### Methods:
- generate_plan()  # main logic
- sort_tasks_by_priority()
- apply_constraints(plan)
- explain_plan(plan)  # optional (for UI explanation)


## Constraint Class
Represents rules that the schedule must follow.

### Attributes:
- max_time_available
- preferred_times (dict or list)
- priority_rules (optional)

### Methods:
- is_task_allowed(task, current_plan)
- check_time_constraint(plan)
- apply(plan)  # modifies or filters plan


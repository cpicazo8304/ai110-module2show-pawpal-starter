"""
app.py

Streamlit front-end for PawPal+ — a daily pet care scheduler.

This module builds the entire user interface and wires it to the
scheduling logic defined in pawpal_system.py. The app is organized
into three main sections:

  1. Profile setup  — owner name, available time slots, and pet registration.
  2. Task entry     — per-pet task form with date, time, duration, and recurrence.
  3. Schedule view  — generated daily plan with sorting, filtering, conflict
                      warnings, mark-complete, and delete controls.

All mutable UI state (pets, tasks, plans) is stored in st.session_state so
it survives Streamlit's top-to-bottom reruns on every user interaction.
"""

import streamlit as st
from pawpal_system import User, Scheduler, Task, Pet, Constraint, DailyPlan
from datetime import datetime, timedelta


# ─────────────────────────────────────────────────────────────────────────────
# Page config
# Sets the browser tab title, favicon, and layout width for the entire app.
# Must be the first Streamlit call in the script.
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.divider()

# ─────────────────────────────────────────────────────────────────────────────
# Section 1 — Profile setup
#
# Collects the owner's name and the time slots they are free during the day.
# selected_times feeds directly into the Constraint object so the scheduler
# knows which start times are permitted.
# ─────────────────────────────────────────────────────────────────────────────
st.subheader("Quick Demo Inputs (UI only)")
owner_name = st.text_input("Owner name", value="")

# Build hour options from 06:00 to 21:00 in one-hour increments.
time_options = [f"{h:02d}:00" for h in range(6, 22)]

selected_times = st.multiselect(
    "Select available time slots",
    options=time_options
)

# ─────────────────────────────────────────────────────────────────────────────
# Pet management
#
# Pets are stored as a list of Pet objects in st.session_state so they
# persist across reruns. Each pet added here becomes a tab in the
# schedule view below.
# ─────────────────────────────────────────────────────────────────────────────
with st.expander("Pets", expanded=True):
    if "pets" not in st.session_state:
        st.session_state.pets = []

    pet_name = st.text_input("Pet name", value="")
    species = st.selectbox("Species", ["dog", "cat", "other"])

    if st.button("Add Pet"):
        if not pet_name or not species:
            st.error("Fill out pet info to add.")
        else:
            pet = Pet(name=pet_name, pet_type=species)
            st.session_state.pets.append(pet)
            st.success(f"Added pet: {pet_name} ({species})")

    # Display a summary of all pets registered so far.
    if st.session_state.pets:
        st.markdown("**Current Pets:**")
        st.write(", ".join([f"{p.name} ({p.pet_type})" for p in st.session_state.pets]))

# ─────────────────────────────────────────────────────────────────────────────
# Profile creation
#
# Builds the User and Constraint objects from the inputs above and stores
# them in session state. Both are required before any tasks can be added
# or schedules generated.
#
# Constraint receives:
#   max_time_available — hard-coded to 300 minutes (5 hours) as a daily cap.
#   available_times    — the time slots the owner selected above.
#
# User receives the same available list so the Scheduler can derive a
# fresh Constraint internally when generating each pet's plan.
# ─────────────────────────────────────────────────────────────────────────────
if "user" not in st.session_state:
    st.session_state.user = None

if st.button("Create Profile"):
    if not owner_name or not pet_name or not species or not selected_times:
        st.error("Please fill in all fields to create a profile.")
    else:
        constraints = Constraint(
            max_time_available=300,
            available_times=selected_times,
        )
        user = User(
            name=owner_name,
            pets=st.session_state.pets,
            time_free=300,
            available=selected_times
        )
        st.session_state.user = user
        st.session_state.constraints = constraints
        st.success(f"Profile created for {st.session_state.user.name}")

# ─────────────────────────────────────────────────────────────────────────────
# Section 2 & 3 — Per-pet task entry and schedule view
#
# Only rendered once both pets and a user profile exist in session state.
# Each pet gets its own tab so multi-pet households stay organized.
# ─────────────────────────────────────────────────────────────────────────────
if st.session_state.pets and st.session_state.user:
    tabs = st.tabs([pet.name for pet in st.session_state.pets])

    for idx, pet in enumerate(st.session_state.pets):
        with tabs[idx]:
            st.subheader(f"Tasks for {pet.name}")

            # tasks_per_pet maps each pet's name to its list of Task objects.
            # Initialized once; individual pet lists are updated on add/delete.
            if "tasks_per_pet" not in st.session_state:
                st.session_state.tasks_per_pet = {p.name: [] for p in st.session_state.pets}

            tasks = st.session_state.tasks_per_pet.get(pet.name, [])

            # ─────────────────────────────────────────────────────────────────
            # Task entry form
            #
            # The user provides a title, duration, date, clock time, and an
            # optional recurrence frequency. start_date and start_time_of_day
            # are combined into a single datetime so Task.start_time carries
            # the full date — required for recurring task scheduling.
            # ─────────────────────────────────────────────────────────────────
            col1, col2, col3 = st.columns(3)
            with col1:
                task_title = st.text_input(f"Task title ({pet.name})", value="", key=f"title_{pet.name}")
            with col2:
                duration = st.number_input(f"Duration (minutes) ({pet.name})", min_value=1, max_value=240, value=20, key=f"duration_{pet.name}")
            col3, col4 = st.columns(2)
            with col3:
                start_date = st.date_input(
                    f"Start date ({pet.name})",
                    value=datetime.today().date(),
                    key=f"date_{pet.name}",
                )
            with col4:
                start_time_of_day = st.time_input(
                    f"Start time ({pet.name})",
                    value=None,
                    key=f"time_{pet.name}",
                )

            # frequency controls whether mark_complete() spawns a follow-up task.
            # "None" means the task is one-off; "daily"/"weekly" enables recurrence.
            frequency = st.selectbox(
                f"Repeat ({pet.name})",
                options=["None", "daily", "weekly"],
                key=f"freq_{pet.name}",
            )

            if st.button(f"Add task for {pet.name}"):
                if not task_title or not start_time_of_day or not duration:
                    st.error("Please fill in all fields to add a task.")
                else:
                    # Combine the date and clock time into a single datetime.
                    # This preserves the calendar date so recurring tasks schedule
                    # correctly across day boundaries using timedelta.
                    start_dt = datetime.combine(start_date, start_time_of_day)
                    new_task = Task(task_type=task_title, 
                                    duration=duration, 
                                    start_time=start_dt,
                                    frequency=None if frequency == "None" else frequency)

                    # Validate the new task against the current plan before adding.
                    # is_task_allowed checks: slot eligibility, overlap, and budget.
                    dummy_plan = DailyPlan(tasks, st.session_state.constraints)
                    if not st.session_state.constraints.is_task_allowed(new_task, dummy_plan):
                        st.error("This task violates your constraints. Please adjust the time or duration.")
                    else:
                        tasks.append(new_task)
                        st.session_state.tasks_per_pet[pet.name] = tasks
                        st.success(
                            f"Added task: {task_title} on "
                            f"{start_dt.strftime('%Y-%m-%d')} at "
                            f"{start_dt.strftime('%H:%M')} for {duration} min"
                        )
            
            if "plan_per_pet" not in st.session_state:
                st.session_state.plan_per_pet = {}

            # ─────────────────────────────────────────────────────────────────
            # Schedule generation
            #
            # Scheduler.generate_plan() sorts tasks chronologically and adds
            # each one after passing the constraint checks, producing a clean
            # DailyPlan. The plan and scheduler are cached in session state
            # so the schedule view below can reference them without rebuilding.
            # ─────────────────────────────────────────────────────────────────
            st.markdown("#### Schedule")

            if tasks:
                scheduler = Scheduler(tasks, st.session_state.user, pet)
                st.session_state.scheduler = scheduler
                plan = scheduler.generate_plan()
                st.session_state.plan_per_pet[pet.name] = plan

            if st.session_state.plan_per_pet.get(pet.name):
                plan = st.session_state.plan_per_pet[pet.name]

                # ─────────────────────────────────────────────────────────────
                # Completion filter toggle
                #
                # When enabled, display_tasks is filtered to exclude any task
                # whose completed flag is True, hiding done items from the view.
                # The underlying plan is unchanged — tasks are not removed.
                # ─────────────────────────────────────────────────────────────
                hide_completed = st.toggle("Hide completed tasks", key=f"hide_{pet.name}")

                display_tasks = (
                    st.session_state.scheduler.filter_tasks_by_completion(plan)
                    if hide_completed
                    else plan.get_tasks()
                )

                # ─────────────────────────────────────────────────────────────
                # Schedule table
                #
                # Each row shows: task name | duration | date+time | status.
                # Two action buttons sit at the end of each row:
                #
                #   ✔️  mark-complete — calls task.mark_complete(), which sets
                #       completed=True and returns a new Task if the frequency
                #       is "daily" or "weekly". The follow-up task is appended
                #       to the task list so it appears in the next plan.
                #
                #   🗑️  delete — removes the task from both the plan and the
                #       underlying task list, then reruns to refresh the view.
                # ─────────────────────────────────────────────────────────────
                st.subheader(f"📅 Daily Plan for {pet.name}")
                for i, task in enumerate(display_tasks):
                    col1, col2, col3, col4, col5, col6 = st.columns([3, 2, 2, 2, 1, 1])
                    col1.write(task.task_type)
                    col2.write(f"{task.duration} min")
                    col3.write(
                        task.start_time.strftime("%m-%d %H:%M")
                        if task.start_time else "-"
                    )

                    col4.write("✅" if task.completed else "❌")

                    # Only show the complete button for tasks not yet done.
                    if not task.completed:
                        if col5.button("✔️", key=f"done_{i}_{pet.name}"):
                            next_task = task.mark_complete()
                            # If the task recurs, append the next occurrence so
                            # it gets picked up on the next generate_plan() call.
                            if next_task:
                                tasks.append(next_task)
                                st.session_state.tasks_per_pet[pet.name] = tasks
                                st.info(
                                    f"Recurring task '{task.task_type}' scheduled "
                                    f"for {next_task.start_time.strftime('%Y-%m-%d')} "
                                    f"at {next_task.start_time.strftime('%H:%M')}."
                                )
                            st.rerun()
                    
                    # Delete removes the task from the live plan and the source
                    # list, then triggers a rerun so the table refreshes cleanly.
                    if col6.button("🗑️", key=f"del_{i}_{pet.name}"):
                        plan.remove_task(task)
                        st.session_state.plan_per_pet[pet.name] = plan
                        tasks.pop(i)
                        st.session_state.tasks_per_pet[pet.name] = tasks
                        st.success("Task deleted.")
                        st.rerun()
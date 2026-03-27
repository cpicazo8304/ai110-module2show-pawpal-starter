import streamlit as st
from pawpal_system import User, Scheduler, Task, Pet, Constraint, DailyPlan
from datetime import datetime, timedelta


st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.divider()

st.subheader("Quick Demo Inputs (UI only)")
owner_name = st.text_input("Owner name", value="")

time_options = [f"{h:02d}:00" for h in range(6, 22)]

selected_times = st.multiselect(
    "Select available time slots",
    options=time_options
)

# Pet management in an expander
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

    # Show current pets
    if st.session_state.pets:
        st.markdown("**Current Pets:**")
        st.write(", ".join([f"{p.name} ({p.pet_type})" for p in st.session_state.pets]))

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

if st.session_state.pets and st.session_state.user:
    tabs = st.tabs([pet.name for pet in st.session_state.pets])

    for idx, pet in enumerate(st.session_state.pets):
        with tabs[idx]:
            st.subheader(f"Tasks for {pet.name}")

            # Initialize per-pet tasks in session state
            if "tasks_per_pet" not in st.session_state:
                st.session_state.tasks_per_pet = {p.name: [] for p in st.session_state.pets}

            tasks = st.session_state.tasks_per_pet.get(pet.name, [])

            # Add a new task for this pet
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

            frequency = st.selectbox(
                f"Repeat ({pet.name})",
                options=["None", "daily", "weekly"],
                key=f"freq_{pet.name}",
            )

            if st.button(f"Add task for {pet.name}"):
                if not task_title or not start_time_of_day or not duration:
                    st.error("Please fill in all fields to add a task.")
                else:
                    start_dt = datetime.combine(start_date, start_time_of_day)
                    new_task = Task(task_type=task_title, 
                                    duration=duration, 
                                    start_time=start_dt,
                                    frequency=None if frequency == "None" else frequency)
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

            # Build schedule for this pet
            st.markdown("#### Schedule")

            if tasks:
                scheduler = Scheduler(tasks, st.session_state.user, pet)
                st.session_state.scheduler = scheduler
                plan = scheduler.generate_plan()
                st.session_state.plan_per_pet[pet.name] = plan


            if st.session_state.plan_per_pet.get(pet.name):
                plan = st.session_state.plan_per_pet[pet.name]

                hide_completed = st.toggle("Hide completed tasks", key=f"hide_{pet.name}")

                display_tasks = (
                    st.session_state.scheduler.filter_tasks_by_completion(plan)
                    if hide_completed
                    else plan.get_tasks()
                )

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

                    if not task.completed:
                        if col5.button("✔️", key=f"done_{i}_{pet.name}"):
                            next_task = task.mark_complete()
                            # If recurring, append the next occurrence to the task list
                            if next_task:
                                tasks.append(next_task)
                                st.session_state.tasks_per_pet[pet.name] = tasks
                                st.info(
                                    f"Recurring task '{task.task_type}' scheduled "
                                    f"for {next_task.start_time.strftime('%Y-%m-%d')} "
                                    f"at {next_task.start_time.strftime('%H:%M')}."
                                )
                            st.rerun()
                    
                    # Delete button per task
                    if col6.button("🗑️", key=f"del_{i}_{pet.name}"):
                        plan.remove_task(task)
                        st.session_state.plan_per_pet[pet.name] = plan
                        tasks.pop(i)
                        st.session_state.tasks_per_pet[pet.name] = tasks
                        st.success("Task deleted.")
                        st.rerun()

# Things to add:
# - add filtering logic (have mark as completed)
# - Automate Recurring Tasks: 
# - Detect Task Conflicts


import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler, Priority

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

# ── Session state ──────────────────────────────────────────────────────────────
if "owner" not in st.session_state:
    st.session_state.owner = None
if "pet" not in st.session_state:
    st.session_state.pet = None
if "tasks" not in st.session_state:
    st.session_state.tasks = []  # list of Task objects

# ── Header ─────────────────────────────────────────────────────────────────────
st.title("🐾 PawPal+")
st.caption("Pet care planning assistant")
st.divider()

# ── 1. Owner ───────────────────────────────────────────────────────────────────
st.subheader("1. Owner")
col1, col2 = st.columns(2)
with col1:
    owner_name = st.text_input("Owner name", value="Jordan")
with col2:
    available_time = st.number_input("Available time (hours)", min_value=0.0, value=3.0, step=0.5)

if st.button("Create Owner"):
    st.session_state.owner = Owner(name=owner_name, available_time=available_time)
    st.success(f"Owner created: {st.session_state.owner.name} ({available_time} hrs available)")

if st.session_state.owner:
    st.info(f"Current owner: **{st.session_state.owner.name}** — {st.session_state.owner.available_time} hrs")

st.divider()

# ── 2. Pet ─────────────────────────────────────────────────────────────────────
st.subheader("2. Add a Pet")
col1, col2, col3 = st.columns(3)
with col1:
    pet_name = st.text_input("Pet name", value="Mochi")
with col2:
    species = st.selectbox("Species", ["dog", "cat", "other"])
with col3:
    pet_age = st.number_input("Age (years)", min_value=0, value=2)

if st.button("Add Pet"):
    st.session_state.pet = Pet(name=pet_name, type=species, age=pet_age)
    st.success(f"Pet added: {st.session_state.pet.name} ({species}, age {pet_age})")

if st.session_state.pet:
    p = st.session_state.pet
    st.info(f"Current pet: **{p.name}** — {p.type}, age {p.age}")

st.divider()

# ── 3. Tasks ───────────────────────────────────────────────────────────────────
st.subheader("3. Tasks")
col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task name", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority_str = st.selectbox("Priority", ["HIGH", "MEDIUM", "LOW"], index=1)

if st.button("Add Task"):
    task = Task(
        name=task_title,
        duration=int(duration),
        priority=Priority[priority_str],
    )
    st.session_state.tasks.append(task)
    st.success(f"Task added: {task.name} ({task.duration} min, {task.priority.name})")

if st.session_state.tasks:
    st.write("Queued tasks:")
    st.table(
        [
            {
                "Task": t.name,
                "Duration (min)": t.duration,
                "Priority": t.priority.name,
            }
            for t in st.session_state.tasks
        ]
    )
    if st.button("Clear Tasks"):
        st.session_state.tasks = []
        st.rerun()
else:
    st.info("No tasks yet. Add one above.")

st.divider()

# ── 4. Generate Schedule ───────────────────────────────────────────────────────
st.subheader("4. Generate Schedule")

if st.button("Generate Schedule"):
    if not st.session_state.owner:
        st.error("Please create an owner first.")
    elif not st.session_state.pet:
        st.error("Please add a pet first.")
    elif not st.session_state.tasks:
        st.error("Please add at least one task.")
    else:
        scheduler = Scheduler(
            owner=st.session_state.owner,
            pet=st.session_state.pet,
        )
        for task in st.session_state.tasks:
            scheduler.add_task(task)

        schedule = scheduler.generate_schedule()

        if schedule:
            st.success("Schedule generated!")
            if schedule.scheduled_tasks:
                st.markdown("**Scheduled tasks:**")
                for task, time_slot in schedule.scheduled_tasks:
                    st.write(f"- {time_slot}: **{task.name}** ({task.duration} min, {task.priority.name})")
            if schedule.unscheduled_tasks:
                st.warning("Tasks that didn't fit:")
                for task in schedule.unscheduled_tasks:
                    st.write(f"- {task.name} ({task.duration} min)")
            if schedule.reasoning:
                with st.expander("Reasoning"):
                    st.write(schedule.reasoning)
        else:
            st.warning("Scheduler returned no schedule. Implement generate_schedule() in pawpal_system.py.")

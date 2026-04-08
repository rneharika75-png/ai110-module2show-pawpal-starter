import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler, Priority

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

# ── Session state ──────────────────────────────────────────────────────────────
if "owner" not in st.session_state:
    st.session_state.owner = None
if "pet" not in st.session_state:
    st.session_state.pet = None
if "tasks" not in st.session_state:
    st.session_state.tasks = []   # list of Task objects

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
    st.success(f"Owner created: **{owner_name}** with {available_time} hrs available today.")

if st.session_state.owner:
    o = st.session_state.owner
    st.info(f"Current owner: **{o.name}** — {o.available_time} hrs available")

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
    st.success(f"Pet added: **{pet_name}** ({species}, age {pet_age})")

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

col4, col5 = st.columns(2)
with col4:
    start_time = st.text_input("Start time (HH:MM, optional)", value="", placeholder="e.g. 08:30")
with col5:
    frequency = st.selectbox("Frequency", ["daily", "weekly", "as-needed"])

if st.button("Add Task"):
    # Validate HH:MM format if provided
    valid_time = True
    clean_time = start_time.strip() or None
    if clean_time:
        parts = clean_time.split(":")
        if len(parts) != 2 or not all(p.isdigit() for p in parts):
            st.error("Start time must be in HH:MM format, e.g. 08:30")
            valid_time = False

    if valid_time:
        task = Task(
            name=task_title,
            duration=int(duration),
            priority=Priority[priority_str],
            frequency=frequency,
            start_time=clean_time,
            pet_id=st.session_state.pet.name if st.session_state.pet else None,
        )
        st.session_state.tasks.append(task)
        time_label = f" at {clean_time}" if clean_time else ""
        st.success(f"Task added: **{task.name}**{time_label} ({task.duration} min, {task.priority.name}, {frequency})")

# ── Task display — sorted by time ──────────────────────────────────────────────
if st.session_state.tasks:
    # Build a temporary scheduler just to use sort_by_time()
    _owner = st.session_state.owner or Owner(name="temp", available_time=24)
    _sched = Scheduler(_owner)
    for t in st.session_state.tasks:
        _sched.add_task(t)
    sorted_tasks = _sched.sort_by_time()

    st.markdown("**Queued tasks** (sorted by start time):")
    st.table(
        [
            {
                "Task": t.name,
                "Start": t.start_time or "—",
                "Duration (min)": t.duration,
                "Priority": t.priority.name,
                "Frequency": t.frequency,
                "Status": "Done" if t.completed else "Pending",
            }
            for t in sorted_tasks
        ]
    )

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("Clear All Tasks"):
            st.session_state.tasks = []
            st.rerun()
    with col_b:
        filter_done = st.checkbox("Show completed tasks only")
    if filter_done:
        done = _sched.filter_tasks(completed=True)
        if done:
            st.info(f"{len(done)} completed task(s):")
            for t in done:
                st.write(f"- {t.name}")
        else:
            st.info("No completed tasks yet.")
else:
    st.info("No tasks yet. Add one above.")

st.divider()

# ── 4. Generate Schedule ───────────────────────────────────────────────────────
st.subheader("4. Generate Schedule")

if st.button("Generate Schedule", type="primary"):
    if not st.session_state.owner:
        st.error("Please create an owner first (Step 1).")
    elif not st.session_state.pet:
        st.error("Please add a pet first (Step 2).")
    elif not st.session_state.tasks:
        st.error("Please add at least one task (Step 3).")
    else:
        scheduler = Scheduler(
            owner=st.session_state.owner,
            pet=st.session_state.pet,
        )
        for task in st.session_state.tasks:
            scheduler.add_task(task)

        # ── Conflict warnings — shown BEFORE the schedule ──────────────────
        conflicts = scheduler.detect_conflicts()
        if conflicts:
            st.warning("**Scheduling conflicts detected — please review before continuing:**")
            for msg in conflicts:
                # Strip the leading "WARNING: " prefix for cleaner display
                clean = msg.replace("WARNING: ", "")
                st.warning(f"⚠️ {clean}")

        # ── Feasibility check ──────────────────────────────────────────────
        feasible, reason = scheduler.validate_feasibility()
        if feasible:
            st.success(f"Time check passed: {reason}")
        else:
            st.error(f"Over time budget — {reason} Some tasks will be skipped.")

        # ── Generate and display ───────────────────────────────────────────
        schedule = scheduler.generate_schedule()

        if schedule.scheduled_tasks:
            st.markdown("---")
            st.markdown("### Today's Plan")
            st.table(
                [
                    {
                        "Time": slot.capitalize(),
                        "Task": task.name,
                        "Duration (min)": task.duration,
                        "Priority": task.priority.name,
                        "Frequency": task.frequency,
                    }
                    for task, slot in schedule.get_tasks_by_time()
                ]
            )
            st.success(
                f"Scheduled **{len(schedule.scheduled_tasks)}** task(s) — "
                f"{schedule.total_time_used:.2f} of {st.session_state.owner.available_time} hrs used."
            )

        if schedule.unscheduled_tasks:
            st.warning(
                f"**{len(schedule.unscheduled_tasks)}** task(s) could not fit in your available time:"
            )
            for task in schedule.unscheduled_tasks:
                st.write(f"- **{task.name}** ({task.duration} min, {task.priority.name})")
            st.caption("Tip: increase your available time or remove a lower-priority task to fit these in.")

        # ── Recurring task next-occurrence summary ─────────────────────────
        recurring = [
            t for t, _ in schedule.scheduled_tasks
            if t.frequency in ("daily", "weekly")
        ]
        if recurring:
            with st.expander("Recurring task schedule"):
                for task in recurring:
                    days = 1 if task.frequency == "daily" else 7
                    from datetime import date, timedelta
                    next_date = date.today() + timedelta(days=days)
                    st.write(f"- **{task.name}** ({task.frequency}) — next due: {next_date}")

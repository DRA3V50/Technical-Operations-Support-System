import sys
import importlib.util
from pathlib import Path
from collections import Counter

import streamlit as st
import pandas as pd
import plotly.express as px

# Project paths
SRC_DIR = Path(__file__).resolve().parent

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from database import initialize, initialize_history
from database import connect

# Load the project's request_service.py under a unique name.
# This avoids conflicts with Python's third-party requests package.
spec = importlib.util.spec_from_file_location(
    "toss_request_service", SRC_DIR / "request_service.py"
)
request_service = importlib.util.module_from_spec(spec)
spec.loader.exec_module(request_service)

PRIORITIES = request_service.PRIORITIES
STATUSES = request_service.STATUSES

# Initialize existing database
@st.cache_resource
def prepare_database():
    initialize()
    initialize_history()
    return True


prepare_database()

st.set_page_config(
    page_title="Technical Operations Support System",
    page_icon="🛠️",
    layout="wide"
)

st.title("Technical Operations Support System")
st.caption(
    "IT Support Management | Live Operational Dashboard"
)

st.divider()


def refresh_with_message(message):
    st.session_state["dashboard_flash"] = message
    st.rerun()


@st.fragment(run_every="15s")
def render_dashboard():

    # Display confirmation after successful changes
    flash = st.session_state.pop("dashboard_flash", None)
    if flash:
        st.success(flash)

    # Retrieve live database records
    records = [
        dict(row) for row in request_service.list_requests()
    ]

    # Operational metrics
    total = len(records)
    closed = sum(r["status"] == "Closed" for r in records)
    outstanding = total - closed
    open_count = sum(r["status"] == "Open" for r in records)
    progress = sum(
        r["status"] == "In Progress" for r in records
    )

    st.subheader("Operational Overview")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Requests", total)
    col2.metric("Outstanding", outstanding)
    col3.metric("Open Requests", open_count)
    col4.metric("Closed Requests", closed)

    st.caption("Dashboard data refreshes automatically every 15 seconds.")

    st.divider()

    # Charts
    st.subheader("Request Analytics")

    if records:
        chart1, chart2 = st.columns(2)

        status_counts = Counter(
            r["status"] for r in records
        )

        priority_counts = Counter(
            r["priority"] for r in records
        )

        status_df = pd.DataFrame([
            {"Status": s, "Requests": n}
            for s, n in status_counts.items()
        ])

        priority_df = pd.DataFrame([
            {"Priority": p, "Requests": priority_counts.get(p, 0)}
            for p in PRIORITIES
        ])

        with chart1:
            fig = px.pie(
                status_df,
                names="Status",
                values="Requests",
                hole=0.45,
                title="Requests by Status"
            )
            st.plotly_chart(fig, width="stretch")

        with chart2:
            fig = px.bar(
                priority_df,
                x="Priority",
                y="Requests",
                color="Priority",
                title="Requests by Priority"
            )
            st.plotly_chart(fig, width="stretch")
    else:
        st.info("Create your first support request to populate analytics.")

    st.divider()

    # Request filters
    st.subheader("Support Request Records")

    filter1, filter2, filter3 = st.columns([2, 1, 1])

    with filter1:
        search = st.text_input(
            "Search requests",
            placeholder="Search title, ID, technician..."
        )

    with filter2:
        selected_statuses = st.multiselect(
            "Filter by status",
            options=list(STATUSES),
            default=list(STATUSES)
        )

    with filter3:
        selected_priorities = st.multiselect(
            "Filter by priority",
            options=list(PRIORITIES),
            default=list(PRIORITIES)
        )

    filtered = []

    for record in records:
        searchable = " ".join(
            str(record.get(field, ""))
            for field in (
                "id", "title", "category",
                "priority", "status", "assigned_to"
            )
        ).lower()

        if (
            record["status"] in selected_statuses
            and record["priority"] in selected_priorities
            and search.lower() in searchable
        ):
            filtered.append(record)

    if filtered:
        display_df = pd.DataFrame(filtered)

        display_df["Request ID"] = display_df["id"].map(
            lambda value: f"SR-{value:04d}"
        )

        display_df = display_df.rename(columns={
            "title": "Issue",
            "category": "Category",
            "priority": "Priority",
            "status": "Status",
            "assigned_to": "Assigned Technician",
            "created_at": "Created",
            "updated_at": "Last Updated"
        })

        display_df = display_df[[
            "Request ID",
            "Issue",
            "Category",
            "Priority",
            "Status",
            "Assigned Technician",
            "Created",
            "Last Updated"
        ]]

        st.dataframe(
            display_df,
            width="stretch",
            hide_index=True
        )
    else:
        st.info("No matching support requests.")

    st.divider()

    # Create request
    st.subheader("Ticket Management")

    with st.expander("Create Support Request"):

        with st.form("create_request_form"):

            title = st.text_input("Issue / Request")
            category = st.text_input("Category")

            priority = st.selectbox(
                "Priority",
                options=list(PRIORITIES)
            )

            submitted = st.form_submit_button(
                "Create Request",
                type="primary"
            )

            if submitted:
                try:
                    new_id = request_service.create_request(
                        title, category, priority
                    )

                    refresh_with_message(
                        f"Request SR-{new_id:04d} created successfully."
                    )

                except ValueError as error:
                    st.error(str(error))

    # Update and close existing requests
    if records:

        with st.expander("Update / Assign / Close Request"):

            record_ids = [r["id"] for r in records]

            selected_id = st.selectbox(
                "Select support request",
                options=record_ids,
                format_func=lambda value: (
                    f"SR-{value:04d} — "
                    f"{next(r['title'] for r in records if r['id'] == value)}"
                )
            )

            selected_record = next(
                r for r in records if r["id"] == selected_id
            )

            st.write(f"**Current status:** {selected_record['status']}")
            st.write(
                f"**Assigned technician:** "
                f"{selected_record['assigned_to']}"
            )

            if selected_record["status"] != "Closed":

                update_col, close_col = st.columns(2)

                with update_col:
                    st.markdown("**Update assignment**")

                    with st.form("update_request_form"):

                        available_statuses = [
                            s for s in STATUSES if s != "Closed"
                        ]

                        new_status = st.selectbox(
                            "New status",
                            options=available_statuses,
                            index=available_statuses.index(
                                selected_record["status"]
                            )
                        )

                        assigned_to = st.text_input(
                            "Assigned technician",
                            value=selected_record["assigned_to"]
                        )

                        update_submitted = st.form_submit_button(
                            "Save Changes"
                        )

                        if update_submitted:
                            try:
                                success = request_service.update_request(
                                    selected_id,
                                    new_status,
                                    assigned_to
                                )

                                if success:
                                    refresh_with_message(
                                        f"SR-{selected_id:04d} updated successfully."
                                    )
                                else:
                                    st.error("Request not found.")

                            except ValueError as error:
                                st.error(str(error))

                with close_col:
                    st.markdown("**Close support request**")

                    with st.form("close_request_form"):

                        resolution = st.text_area(
                            "Resolution notes",
                            placeholder=(
                                "Describe the troubleshooting performed "
                                "and how the issue was resolved."
                            )
                        )

                        close_submitted = st.form_submit_button(
                            "Close Request"
                        )

                        if close_submitted:
                            try:
                                success = request_service.close_request(
                                    selected_id,
                                    resolution
                                )

                                if success:
                                    refresh_with_message(
                                        f"SR-{selected_id:04d} closed successfully."
                                    )
                                else:
                                    st.error("Request not found.")

                            except ValueError as error:
                                st.error(str(error))

            else:
                st.info("This request is already closed.")

            # Request history
            st.markdown("**Request History**")

            history = request_service.get_request_history(
                selected_id
            )

            if history:
                history_df = pd.DataFrame([
                    dict(entry) for entry in history
                ])

                st.dataframe(
                    history_df,
                    width="stretch",
                    hide_index=True
                )
            else:
                st.info("No history available.")

    else:
        st.info("There are currently no requests to manage.")


render_dashboard()

st.divider()

st.caption(
    "TOSS | Technical Operations Support System | "
    "Python • SQLite • Streamlit • Plotly"
)

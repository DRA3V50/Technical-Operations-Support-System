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

st.markdown(
    """
    <style>
    .stApp { background-color: #f3f6fb; }
    [data-testid="stHeader"] { background: transparent; }
    .block-container {
        max-width: 1560px;
        padding-top: 1.8rem;
        padding-bottom: 2rem;
    }
    .toss-hero {
        padding: 1.9rem 2rem;
        margin-bottom: 1.5rem;
        border-radius: 20px;
        background: linear-gradient(
            120deg, #10243e 0%, #173f5f 60%, #0f766e 100%
        );
        box-shadow: 0 8px 24px rgba(16, 36, 62, 0.14);
        color: white;
    }
    .toss-kicker {
        color: #a9d5d8;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.16em;
        margin-bottom: 0.65rem;
    }
    .toss-heading {
        color: #ffffff;
        font-size: 2.15rem;
        font-weight: 750;
        line-height: 1.15;
    }
    .toss-subheading {
        color: #d7e5f0;
        font-size: 0.98rem;
        margin-top: 0.55rem;
    }
    .toss-live {
        display: inline-flex;
        align-items: center;
        gap: 0.55rem;
        margin-top: 1.1rem;
        padding: 0.4rem 0.8rem;
        border: 1px solid rgba(255,255,255,0.2);
        border-radius: 30px;
        background: rgba(255,255,255,0.1);
        color: #e2f7ef;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.06em;
    }
    .toss-live-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #5ee0a0;
        display: inline-block;
    }
    div[data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid #e5ebf3;
        border-radius: 16px;
        padding: 1rem 1.15rem;
        min-height: 112px;
        box-shadow: 0 4px 14px rgba(20, 40, 70, 0.05);
    }
    div[data-testid="stMetricLabel"] p {
        color: #64748b;
        font-size: 0.82rem;
        font-weight: 650;
    }
    div[data-testid="stMetricValue"] {
        color: #102a43;
        font-weight: 750;
    }
    h2, h3 { color: #102a43; }
    div[data-testid="stExpander"] {
        background: #ffffff;
        border: 1px solid #e5ebf3;
        border-radius: 14px;
    }
    div[data-testid="stDataFrame"] {
        border: 1px solid #e5ebf3;
        border-radius: 12px;
        overflow: hidden;
    }
    .stButton > button,
    div[data-testid="stFormSubmitButton"] button {
        border-radius: 10px;
        font-weight: 650;
    }
    hr { border-color: #e4eaf2; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="toss-hero">
        <div class="toss-kicker">
            IT SERVICE MANAGEMENT · OPERATIONS CENTER
        </div>
        <div class="toss-heading">
            Technical Operations Support
        </div>
        <div class="toss-subheading">
            A live view of service requests, incident priorities,
            and support activity.
        </div>
        <div class="toss-live">
            <span class="toss-live-dot"></span>
            LIVE OPERATIONAL DATA
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


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
    progress = sum(
        r["status"] == "In Progress" for r in records
    )
    critical_active = sum(
        r["priority"] == "Critical" and r["status"] != "Closed"
        for r in records
    )

    st.subheader("Operational Overview")

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("Total Requests", total)
    col2.metric("Active Requests", outstanding)
    col3.metric("Critical Active", critical_active)
    col4.metric("In Progress", progress)
    col5.metric("Closed Requests", closed)

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
            fig.update_traces(
                textfont_color="#ffffff",
                marker_line_color="#ffffff",
                marker_line_width=2
            )
            fig.update_layout(
                paper_bgcolor="#ffffff",
                plot_bgcolor="#ffffff",
                font=dict(color="#334155", family="Arial", size=12),
                title_font=dict(color="#102a43", size=16),
                margin=dict(l=20, r=20, t=55, b=20),
                height=340
            )
            st.plotly_chart(fig, width="stretch")

        with chart2:
            fig = px.bar(
                priority_df,
                x="Priority",
                y="Requests",
                color="Priority",
                color_discrete_map={
                    "Low": "#0f766e",
                    "Medium": "#3b82f6",
                    "High": "#f59e0b",
                    "Critical": "#dc2626"
                },
                title="Requests by Priority"
            )
            fig.update_layout(
                paper_bgcolor="#ffffff",
                plot_bgcolor="#ffffff",
                font=dict(color="#334155", family="Arial", size=12),
                title_font=dict(color="#102a43", size=16),
                margin=dict(l=20, r=20, t=55, b=20),
                height=340
            )
            fig.update_xaxes(showgrid=False)
            fig.update_yaxes(
                showgrid=True,
                gridcolor="#e8edf3",
                zeroline=False,
                rangemode="tozero"
            )
            st.plotly_chart(fig, width="stretch")
    else:
        st.info("Create your first support request to populate analytics.")

    st.divider()

    # System Health Monitoring
    st.subheader("System Health Monitoring")

    import sqlite3
    import time
    from datetime import datetime
    from monitor_store import DB_PATH

    readings = []

    if DB_PATH.exists():
        try:
            with sqlite3.connect(DB_PATH) as db:
                readings = db.execute("""
                    SELECT observed_at, cpu_percent,
                           memory_percent, disk_percent
                    FROM system_metrics
                    ORDER BY observed_at DESC, id DESC
                    LIMIT 400
                """).fetchall()
        except sqlite3.Error as error:
            st.warning(f"Monitoring data unavailable: {error}")

    if readings:
        readings.reverse()
        latest = readings[-1]

        observed_at, cpu, memory, disk = latest
        age_minutes = max(
            0, (time.time() - observed_at) / 60
        )

        if age_minutes > 75:
            st.warning(
                "Monitoring data is outdated. "
                "Check the TOSS background service."
            )
        else:
            st.caption("Ubuntu WSL monitoring is active.")

        health1, health2, health3 = st.columns(3)

        health1.metric("CPU Usage", f"{cpu:.1f}%")
        health2.metric("Memory Usage", f"{memory:.1f}%")
        health3.metric("Disk Usage", f"{disk:.1f}%")

        last_check = datetime.fromtimestamp(
            observed_at
        ).strftime("%b %d, %Y at %I:%M %p")

        st.caption(
            f"Last measurement: {last_check} "
            f"(Ubuntu local time) · "
            f"{len(readings)} stored readings"
        )

        if cpu >= 95 or memory >= 90 or disk >= 90:
            st.warning(
                "One or more measurements exceed "
                "the monitoring thresholds."
            )

        history = pd.DataFrame(
            readings,
            columns=[
                "Timestamp", "CPU",
                "Memory", "Disk"
            ]
        )

        history["Timestamp"] = history["Timestamp"].map(
            datetime.fromtimestamp
        )

        fig = px.line(
            history,
            x="Timestamp",
            y=["CPU", "Memory", "Disk"],
            title="System Resource History",
            labels={
                "value": "Usage (%)",
                "variable": "Resource"
            },
            color_discrete_map={
                "CPU": "#3b82f6",
                "Memory": "#0f766e",
                "Disk": "#f59e0b"
            }
        )

        fig.update_layout(
            paper_bgcolor="#ffffff",
            plot_bgcolor="#ffffff",
            font=dict(color="#334155", size=12),
            title_font=dict(color="#102a43", size=16),
            margin=dict(l=20, r=20, t=55, b=20),
            height=340,
            legend_title_text=""
        )

        fig.update_yaxes(
            range=[0, 100],
            gridcolor="#e8edf3"
        )

        st.plotly_chart(fig, width="stretch")

    else:
        st.info(
            "No monitoring readings available yet."
        )

    st.caption(
        "System measurements are collected every 30 minutes. "
        "These readings describe Ubuntu WSL, not the entire Windows PC."
    )

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

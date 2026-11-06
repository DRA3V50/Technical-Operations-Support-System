import sqlite3
import time

from database import initialize, initialize_history
from monitor_store import DB_PATH, save_metrics
import request_service as service


THRESHOLDS = {
    "cpu_percent": (95, "High", "High CPU usage"),
    "memory_percent": (90, "High", "High memory usage"),
    "disk_percent": (90, "Critical", "Low disk space"),
}


def check_alerts():
    initialize()
    initialize_history()

    save_metrics()

    with sqlite3.connect(DB_PATH) as db:
        db.row_factory = sqlite3.Row
        readings = db.execute("""
            SELECT observed_at, cpu_percent,
                   memory_percent, disk_percent
            FROM system_metrics
            ORDER BY id DESC
            LIMIT 2
        """).fetchall()

    if len(readings) < 2:
        print("Waiting for another monitoring reading.")
        return

    latest, previous = readings

    interval = latest["observed_at"] - previous["observed_at"]

    if not 1200 <= interval <= 2700:
        print("Waiting for two readings 20-45 minutes apart.")
        return

    if time.time() - latest["observed_at"] > 120:
        print("Latest reading is too old.")
        return

    for metric, (limit, priority, description) in THRESHOLDS.items():
        if not (
            latest[metric] >= limit
            and previous[metric] >= limit
        ):
            continue

        title = f"[AUTO][WSL] {description}"

        existing = [
            ticket for ticket in service.list_requests()
            if ticket["title"] == title
            and ticket["status"] != "Closed"
        ]

        if existing:
            print(f"Existing active ticket: {title}")
            continue

        request_id = service.create_request(
            title,
            "System Monitoring",
            priority,
        )

        print(
            f"Automatic ticket created: SR-{request_id:04d}"
        )

    print("Monitoring alert check completed.")


if __name__ == "__main__":
    check_alerts()

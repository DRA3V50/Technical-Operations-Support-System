from collections import Counter
from datetime import datetime
from pathlib import Path

from database import connect


REPORT_DIR = Path(__file__).resolve().parent.parent / "reports"


def generate_report():
    with connect() as db:
        records = [
            dict(row) for row in db.execute(
                "SELECT * FROM requests ORDER BY id"
            ).fetchall()
        ]

    counts = Counter(r["status"] for r in records)
    outstanding = [
        r for r in records if r["status"] != "Closed"
    ]

    lines = [
        "TECHNICAL OPERATIONS SUPPORT SYSTEM",
        "OPERATIONAL REPORT",
        "=" * 48,
        f"Generated: {datetime.now().astimezone().isoformat(timespec='seconds')}",
        f"Total requests: {len(records)}",
        f"Closed requests: {counts['Closed']}",
        f"Outstanding requests: {len(outstanding)}",
        "",
        "REQUEST STATUS SUMMARY",
        "-" * 48,
    ]

    for status, count in sorted(counts.items()):
        lines.append(f"{status}: {count}")

    lines.extend([
        "",
        "OUTSTANDING REQUESTS",
        "-" * 48,
    ])

    if not outstanding:
        lines.append("No outstanding requests.")
    else:
        for r in outstanding:
            lines.extend([
                f"SR-{r['id']:04d} | {r['priority']} | {r['status']}",
                f"  Issue: {r['title']}",
                f"  Assigned: {r['assigned_to']}",
                f"  Last updated: {r['updated_at']}",
                "",
            ])

    return "\n".join(lines)


def export_report():
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    path = REPORT_DIR / f"operations_{timestamp}.txt"
    path.write_text(generate_report() + "\n", encoding="utf-8")
    return path

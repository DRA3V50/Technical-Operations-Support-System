from database import connect
from request_service import PRIORITIES, STATUSES

MIN_RESOLUTION_LENGTH = 15


def valid_resolution(text):
    text = (text or "").strip()
    return (
        len(text) >= MIN_RESOLUTION_LENGTH
        and len(text.split()) >= 3
    )


def review_records():
    with connect() as db:
        records = db.execute(
            "SELECT * FROM requests ORDER BY id"
        ).fetchall()

    findings = []

    for record in records:
        issues = []

        if not (record["title"] or "").strip():
            issues.append("Missing request title")

        if not (record["category"] or "").strip():
            issues.append("Missing category")

        if record["priority"] not in PRIORITIES:
            issues.append("Invalid priority")

        if record["status"] not in STATUSES:
            issues.append("Invalid status")

        if record["status"] in (
            "Assigned", "In Progress",
            "Escalated", "Resolved", "Closed"
        ):
            if not (record["assigned_to"] or "").strip() or (
                record["assigned_to"] == "Unassigned"
            ):
                issues.append("Missing assignment")

        if record["status"] == "Closed":
            if not valid_resolution(record["resolution"]):
                issues.append("Incomplete resolution notes")

        if issues:
            findings.append({
                "id": record["id"],
                "title": record["title"],
                "issues": issues
            })

    return len(records), findings


def correct_resolution(request_id, resolution):
    if not valid_resolution(resolution):
        raise ValueError(
            "Resolution must contain at least "
            "15 characters and 3 words."
        )

    with connect() as db:
        record = db.execute(
            "SELECT status FROM requests WHERE id = ?",
            (request_id,)
        ).fetchone()

        if record is None:
            return False

        if record["status"] not in ("Resolved", "Closed"):
            raise ValueError(
                "Only resolved or closed requests "
                "can have their resolution corrected."
            )

        db.execute("""
            UPDATE requests
            SET resolution = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (resolution.strip(), request_id))

    return True

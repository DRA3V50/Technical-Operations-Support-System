from database import connect

PRIORITIES = ("Low", "Medium", "High", "Critical")
STATUSES = ("Open", "Assigned", "In Progress",
            "Pending", "Escalated", "Resolved", "Closed")


def create_request(title, category, priority):
    if not title.strip() or not category.strip():
        raise ValueError("Title and category are required.")

    if priority not in PRIORITIES:
        raise ValueError("Invalid priority.")

    with connect() as db:
        cursor = db.execute("""
            INSERT INTO requests (title, category, priority)
            VALUES (?, ?, ?)
        """, (title.strip(), category.strip(), priority))
        return cursor.lastrowid


def list_requests():
    with connect() as db:
        return db.execute(
            "SELECT * FROM requests ORDER BY id DESC"
        ).fetchall()


def get_request(request_id):
    with connect() as db:
        return db.execute(
            "SELECT * FROM requests WHERE id = ?",
            (request_id,)
        ).fetchone()


def update_request(request_id, status, assigned_to):
    if status not in STATUSES:
        raise ValueError("Invalid status.")

    if not assigned_to.strip():
        raise ValueError("Assignee is required.")

    with connect() as db:
        cursor = db.execute("""
            UPDATE requests
            SET status = ?, assigned_to = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (status, assigned_to.strip(), request_id))
        return cursor.rowcount > 0


def close_request(request_id, resolution):
    if not resolution.strip():
        raise ValueError("A resolution is required.")

    with connect() as db:
        cursor = db.execute("""
            UPDATE requests
            SET status = 'Closed',
                resolution = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (resolution.strip(), request_id))
        return cursor.rowcount > 0


def get_request_history(request_id):
    with connect() as db:
        return db.execute("""
            SELECT action, details, recorded_at
            FROM request_history
            WHERE request_id = ?
            ORDER BY id ASC
        """, (request_id,)).fetchall()

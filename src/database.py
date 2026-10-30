import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "toss.db"


def connect():
    DB_PATH.parent.mkdir(exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize():
    with connect() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                category TEXT NOT NULL,
                priority TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Open',
                assigned_to TEXT NOT NULL DEFAULT 'Unassigned',
                resolution TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)


def initialize_history():
    with connect() as db:
        db.execute("DROP TRIGGER IF EXISTS log_request_updated")
        db.executescript("""
            CREATE TABLE IF NOT EXISTS request_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                request_id INTEGER NOT NULL,
                action TEXT NOT NULL,
                details TEXT NOT NULL,
                recorded_at TEXT NOT NULL
                    DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (request_id)
                    REFERENCES requests(id)
            );

            CREATE TRIGGER IF NOT EXISTS log_request_created
            AFTER INSERT ON requests
            BEGIN
                INSERT INTO request_history
                    (request_id, action, details)
                VALUES (
                    NEW.id,
                    'Created',
                    'Priority: ' || NEW.priority ||
                    ' | Status: ' || NEW.status
                );
            END;

            CREATE TRIGGER IF NOT EXISTS log_request_updated
            AFTER UPDATE ON requests
            WHEN OLD.status IS NOT NEW.status
              OR OLD.assigned_to IS NOT NEW.assigned_to
              OR OLD.resolution IS NOT NEW.resolution
            BEGIN
                INSERT INTO request_history
                    (request_id, action, details)
                VALUES (
                    NEW.id,
                    CASE
                        WHEN OLD.status = 'Closed'
                             AND NEW.status = 'Closed'
                             AND OLD.resolution IS NOT NEW.resolution
                        THEN 'Resolution Corrected'
                        WHEN OLD.status != 'Closed'
                             AND NEW.status = 'Closed'
                        THEN 'Closed'
                        ELSE 'Updated'
                    END,
                    'Status: ' || OLD.status ||
                    ' -> ' || NEW.status ||
                    ' | Assigned: ' || NEW.assigned_to ||
                    ' | Resolution: ' ||
                    COALESCE(NULLIF(NEW.resolution, ''), 'None')
                );
            END;
        """)

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from monitor import collect_metrics

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "monitoring.db"
MAX_RECORDS = 400
RETENTION_DAYS = 7
MAX_DB_BYTES = 10 * 1024 * 1024


def save_metrics():
    metrics = collect_metrics()
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(DB_PATH) as db:
        db.execute("PRAGMA auto_vacuum = FULL")

        db.execute("""
            CREATE TABLE IF NOT EXISTS system_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                observed_at INTEGER NOT NULL,
                cpu_percent REAL NOT NULL,
                memory_percent REAL NOT NULL,
                disk_percent REAL NOT NULL
            )
        """)

        page_size = db.execute(
            "PRAGMA page_size"
        ).fetchone()[0]

        db.execute(
            f"PRAGMA max_page_count = {MAX_DB_BYTES // page_size}"
        )

        now = int(datetime.now(timezone.utc).timestamp())
        cutoff = now - RETENTION_DAYS * 86400

        db.execute(
            "DELETE FROM system_metrics WHERE observed_at < ?",
            (cutoff,)
        )

        db.execute("""
            DELETE FROM system_metrics
            WHERE id NOT IN (
                SELECT id FROM system_metrics
                ORDER BY id DESC LIMIT ?
            )
        """, (MAX_RECORDS - 1,))

        db.execute("""
            INSERT INTO system_metrics
                (observed_at, cpu_percent,
                 memory_percent, disk_percent)
            VALUES (?, ?, ?, ?)
        """, (
            now,
            metrics["cpu_percent"],
            metrics["memory_percent"],
            metrics["disk_percent"]
        ))

        count = db.execute(
            "SELECT COUNT(*) FROM system_metrics"
        ).fetchone()[0]

    print(f"Monitoring record saved. Total records: {count}")
    print(f"Database size: {DB_PATH.stat().st_size:,} bytes")


if __name__ == "__main__":
    save_metrics()

import sqlite3
from datetime import datetime, timezone

from config import DATABASE_PATH


def log_event(event, username=None, result="success", details=None):
    """Spara en säkerhetshändelse i den lokala SQLite-databasen."""

    timestamp = datetime.now(timezone.utc).isoformat()

    connection = sqlite3.connect(DATABASE_PATH)

    try:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                event TEXT NOT NULL,
                username TEXT,
                result TEXT NOT NULL,
                details TEXT
            )
            """
        )

        connection.execute(
            """
            INSERT INTO audit_logs (
                timestamp, event, username, result, details
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (timestamp, event, username, result, details),
        )

        connection.commit()

    finally:
        connection.close()

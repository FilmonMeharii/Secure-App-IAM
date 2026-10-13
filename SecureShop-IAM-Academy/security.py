import sqlite3
from datetime import datetime, timedelta, timezone

from config import DATABASE_PATH


MAX_FAILED_ATTEMPTS = 5
LOCKOUT_MINUTES = 5


def is_login_locked(username):
    """Kontrollera om användaren har för många misslyckade försök."""

    if not username:
        return False

    cutoff = (
        datetime.now(timezone.utc)
        - timedelta(minutes=LOCKOUT_MINUTES)
    ).isoformat()

    with sqlite3.connect(DATABASE_PATH) as connection:
        row = connection.execute(
            """
            SELECT COUNT(*)
            FROM audit_logs
            WHERE username = ?
              AND event = 'login_failed'
              AND timestamp >= ?
            """,
            (username, cutoff),
        ).fetchone()

    return row[0] >= MAX_FAILED_ATTEMPTS

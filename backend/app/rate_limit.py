from .db import get_db
from datetime import datetime

def get_rate_limit(scope, rate_limit_key):
    db = get_db()

    record = db.execute(
        """
        SELECT
            id,
            scope,
            rate_limit_key,
            attempt_count,
            window_started_at,
            blocked_until,
            updated_at
        FROM login_rate_limits
        WHERE scope = ?
            AND rate_limit_key = ?
        """,
        (scope, rate_limit_key),
    ).fetchone()

    return record

def create_rate_limit(scope, rate_limit_key, attempt_count=0):
    db = get_db()

    db.execute(
        """
        INSERT INTO login_rate_limits(
            scope,
            rate_limit_key,
            attempt_count
        )
        VALUES (?, ?, ?)
        """,
        (
            scope,
            rate_limit_key,
            attempt_count,
        ),
        
    )

    db.commit()

def increment_rate_limit(scope, rate_limit_key):
    db = get_db()

    db.execute(
        """
        UPDATE login_rate_limits
        SET attempt_count = attempt_count + 1,
            updated_at = CURRENT_TIMESTAMP
        WHERE scope = ?
            AND rate_limit_key = ?
        """,
        (
            scope,
            rate_limit_key,
        ),
    )

    db.commit()

def reset_rate_limit(scope, rate_limit_key):
    db = get_db()

    db.execute(
        """
        DELETE FROM login_rate_limits
        WHERE scope = ?
            AND rate_limit_key = ?
        """,
        (
            scope,
            rate_limit_key,
        ),
    )

    db.commit()

def block_rate_limit(scope, rate_limit_key, blocked_until):
    db = get_db()

    db.execute(
        """
        UPDATE login_rate_limits
        SET blocked_until = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE scope = ?
            AND rate_limit_key = ?
        """,
        (
            blocked_until,
            scope,
            rate_limit_key,
        )
    ),

    db.commit()

def is_rate_limit_blocked(record, current_time):
    if record["blocked_until"] is None:
        return False

    blocked_until = datetime.fromisoformat(
        record["blocked_until"]
    )

    return current_time < blocked_until

def has_rate_limit_window_expired(record, current_time):
    if record["window_started_at"] is None:
        return False

    window_started_at = datetime.fromisoformat(
        record["window_started_at"]
    )

    elapsed = current_time - window_started_at

    return elapsed.total_seconds() >= 60 
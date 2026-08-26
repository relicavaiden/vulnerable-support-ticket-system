from .db import get_db
from datetime import datetime, timedelta

IP_USERNAME_MAX_ATTEMPTS = 5
IP_MAX_ATTEMPTS = 20

RATE_LIMIT_WINDOW_SECONDS = 60
RATE_LIMIT_COOLDOWN_SECONDS = 60

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

def create_rate_limit(scope, rate_limit_key, attempt_count=0, window_started_at=None):
    db = get_db()

    if window_started_at is None:
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
    else:
        window_started_at_value = window_started_at.isoformat(sep=" ")

        db.execute(
            """
            INSERT INTO login_rate_limits(
            scope,
            rate_limit_key,
            attempt_count,
            window_started_at
            )
            VALUES(?, ?, ?, ?)
            """,
            (
                scope,
                rate_limit_key,
                attempt_count,
                window_started_at_value,
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

    blocked_until_value = blocked_until.isoformat(sep=" ")

    db.execute(
        """
        UPDATE login_rate_limits
        SET blocked_until = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE scope = ?
            AND rate_limit_key = ?
        """,
        (
            blocked_until_value,
            scope,
            rate_limit_key,
        )
    )

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

def record_rate_limit_attempt(scope, rate_limit_key, current_time):
    record = get_rate_limit(
        scope,
        rate_limit_key,
    )

    if record is None:
        create_rate_limit(
            scope,
            rate_limit_key,
            1,
            current_time,
        )

        return get_rate_limit(
            scope,
            rate_limit_key,
        )

    if has_rate_limit_window_expired(record, current_time):
        reset_rate_limit(
            scope,
            rate_limit_key,
        )

        create_rate_limit(
            scope,
            rate_limit_key,
            1,
            current_time,
        )

        return get_rate_limit(
            scope,
            rate_limit_key,
        )
    else:
        increment_rate_limit(
            scope,
            rate_limit_key,
        )

        return get_rate_limit(
            scope,
            rate_limit_key,
        )

def has_rate_limit_reached_threshold(record, max_attempts):
    return record["attempt_count"] >= max_attempts

def apply_rate_limit_threshold(
        record,
        current_time,
):
    cooldown_seconds = RATE_LIMIT_COOLDOWN_SECONDS
    max_attempts = get_rate_limit_max_attempts(
        record["scope"]
    )

    if has_rate_limit_reached_threshold(
        record,
        max_attempts,
    ) is False:
        return False
    

    blocked_until = current_time + timedelta(seconds=cooldown_seconds)

    block_rate_limit(
        record["scope"],
        record["rate_limit_key"],
        blocked_until,
    )
    return True

def get_rate_limit_max_attempts(scope):
    if scope == "ip_username":
        return IP_USERNAME_MAX_ATTEMPTS

    if scope == "ip":
        return IP_MAX_ATTEMPTS

    if scope not in {"ip_username", "ip"}:
        raise ValueError("Invalid rate-limit scope")

def record_and_apply_rate_limit(scope, rate_limit_key, current_time):
    record = record_rate_limit_attempt(
        scope,
        rate_limit_key,
        current_time,
    )

    apply_rate_limit_threshold(
        record,
        current_time,
    )

    return get_rate_limit(
        scope,
        rate_limit_key,
    )
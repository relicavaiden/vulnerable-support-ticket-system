from app.db import get_db, init_db
from app.rate_limit import get_rate_limit, create_rate_limit, increment_rate_limit, reset_rate_limit, block_rate_limit, is_rate_limit_blocked, has_rate_limit_window_expired

from datetime import datetime, timedelta

def test_get_rate_limit_returns_none_when_record_does_not_exist(app):
    with app.app_context():
        init_db()

        record = get_rate_limit(
            "ip",
            "192.168.1.20",
        )

        assert record is None

def test_get_rate_limit_returns_scope_key_and_count(app):
    with app.app_context():
        init_db()

        db = get_db()

        rate_limit_cursor = db.execute(
            """
            INSERT INTO login_rate_limits(
                scope,
                rate_limit_key,
                attempt_count
            )
            VALUES(?, ?, ?)
            """,
            (
                "ip",
                "192.168.1.20",
                3,
            ),
        )

        db.commit()

        record = get_rate_limit(
            "ip",
            "192.168.1.20",
        )

        assert record is not None
        assert record["scope"] == "ip"
        assert record["rate_limit_key"] == "192.168.1.20"
        assert record["attempt_count"] == 3

def test_create_rate_limit_creates_record(app):
    with app.app_context():
        init_db()

        create_rate_limit(
            "ip",
            "192.168.1.20",
            1,
        )

        record = get_rate_limit(
            "ip",
            "192.168.1.20",
        )

        assert record is not None
        assert record["scope"] == "ip"
        assert record["rate_limit_key"] == "192.168.1.20"
        assert record["attempt_count"] == 1

def test_increment_rate_limit_updates_record(app):
    with app.app_context():
        init_db()

        create_rate_limit(
            "ip",
            "192.168.1.20",
            1,
        )

        increment_rate_limit(
            "ip",
            "192.168.1.20",
        )

        record = get_rate_limit(
            "ip",
            "192.168.1.20",
        )

        assert record is not None
        assert record["scope"] == "ip"
        assert record["rate_limit_key"] == "192.168.1.20"
        assert record["attempt_count"] == 2

def test_reset_rate_limit_deletes_records(app):
    with app.app_context():
        init_db()

        create_rate_limit(
            "ip",
            "192.168.1.20",
            3,
        )

        record = get_rate_limit(
            "ip",
            "192.168.1.20",
        )

        assert record is not None

        reset_rate_limit(
            "ip",
            "192.168.1.20",
        )

        record = get_rate_limit(
            "ip",
            "192.168.1.20",
        )

        assert record is None

def test_block_rate_limit_returns_time(app):
    with app.app_context():
        init_db()

        create_rate_limit (
            "ip",
            "192.168.1.20",
            20,
        )

        block_rate_limit(
            "ip",
            "192.168.1.20",
            "2026-10-31 23:00:00",
        )

        record = get_rate_limit(
            "ip",
            "192.168.1.20",
        )

        assert record is not None
        assert record["blocked_until"] == "2026-10-31 23:00:00"

def test_is_rate_limit_blocked_returns_false(app):
    with app.app_context():
        init_db()

        create_rate_limit(
            "ip",
            "192.168.1.20",
            1,
        )

        record = get_rate_limit(
            "ip",
            "192.168.1.20",
        )

        current_time = datetime(
            2026,
            8,
            20,
            14,
            0,
            0,
        )

        assert record is not None
        assert is_rate_limit_blocked(record, current_time) is False

def test_is_rate_limit_blocked_returns_true(app):
    with app.app_context():
        init_db()

        create_rate_limit(
            "ip",
            "192.168.1.20",
        )

        block_rate_limit(
            "ip",
            "192.168.1.20",
            "2026-08-10 23:10:00",
        )

        record = get_rate_limit(
            "ip",
            "192.168.1.20",
        )

        current_time = datetime(
            2026,
            8,
            10,
            23,
            0,
            0,
        )

        assert record is not None
        assert is_rate_limit_blocked(record, current_time) is True

def test_is_rate_limit_blocked_returns_false_at_expiry(app):
    with app.app_context():
        init_db()

        create_rate_limit(
            "ip",
            "192.168.1.20"
        )

        block_rate_limit(
            "ip",
            "192.168.1.20",
            "2026-08-20 23:00:00"
        )

        record = get_rate_limit(
            "ip",
            "192.168.1.20"
        )

        current_time = datetime(
            2026,
            8,
            20,
            23,
            0,
            0,
        )

        assert record is not None
        assert is_rate_limit_blocked(record, current_time) is False

def test_has_rate_limit_window_expired_at_thirty_seconds_returns_false(app):
    with app.app_context():
        init_db()

        create_rate_limit(
            "ip",
            "192.168.1.20",
        )

        record = get_rate_limit(
            "ip",
            "192.168.1.20",
        )

        assert record is not None

        window_started_at = datetime.fromisoformat(
            record["window_started_at"]
        )
        
        current_time = window_started_at + timedelta(seconds=30)

        assert has_rate_limit_window_expired(record, current_time) is False

def test_has_rate_limit_window_expired_at_sixty_seconds_returns_true(app):
    with app.app_context():
        init_db()

        create_rate_limit(
            "ip",
            "192.168.1.20",
        )

        record = get_rate_limit(
            "ip",
            "192.168.1.20"
        )

        assert record is not None

        window_started_at = datetime.fromisoformat(
            record["window_started_at"]
        )

        current_time = window_started_at + timedelta(seconds=60)

        assert has_rate_limit_window_expired(record, current_time) is True
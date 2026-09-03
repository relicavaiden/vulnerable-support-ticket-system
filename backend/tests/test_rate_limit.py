from app.db import get_db, init_db
from app.rate_limit import RATE_LIMIT_COOLDOWN_SECONDS, get_rate_limit, create_rate_limit, increment_rate_limit, reset_rate_limit, block_rate_limit, is_rate_limit_blocked, has_rate_limit_window_expired, record_rate_limit_attempt, has_rate_limit_reached_threshold, apply_rate_limit_threshold, get_rate_limit_max_attempts,record_and_apply_rate_limit

from datetime import datetime, timedelta
import pytest

from app.seed import seed_db

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
        blocked_until = datetime(
            2026,
            10,
            31,
            23,
            0,
            0,
        )

        block_rate_limit(
            "ip",
            "192.168.1.20",
            blocked_until,
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

        blocked_until = datetime(
            2026,
            8,
            20,
            23,
            0,
            0,
        )

        block_rate_limit(
            "ip",
            "192.168.1.20",
            blocked_until,
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

        blocked_until = datetime(
            2026,
            8,
            20,
            23,
            0,
            0,
        )

        block_rate_limit(
            "ip",
            "192.168.1.20",
            blocked_until,
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

def test_check_current_window_attempts(app):
    with app.app_context():
        init_db()

        current_time = datetime (
            2026,
            8,
            30,
            23,
            0,
            0
        )

        record = record_rate_limit_attempt(
            "ip",
            "192.168.1.20",
            current_time,
            )

        assert record is not None
        assert record["attempt_count"] == 1

        stored_window_start = datetime.fromisoformat(
            record["window_started_at"]
        )
        assert stored_window_start == current_time

def test_window_resets_with_new_current_time(app):
    with app.app_context():
        init_db()

        old_time = datetime(
            2026,
            8,
            30,
            23,
            0,
            0
        )

        create_rate_limit(
            "ip",
            "192.168.1.20",
            4,
            window_started_at= old_time,
        )

        current_time = datetime(
           2026,
           8,
           30,
           23,
           1,
           0
       )

        record = record_rate_limit_attempt(
            "ip",
            "192.168.1.20",
            current_time,
        )

        assert record is not None
        assert record["attempt_count"] == 1

        stored_window_start = datetime.fromisoformat(
            record["window_started_at"]
        )
        assert stored_window_start == current_time

def test_count_updates_while_window_is_still_active(app):
    with app.app_context():
        init_db()

        old_time = datetime(
            2026,
            8,
            30,
            23,
            0,
            0
        )

        create_rate_limit(
            "ip",
            "192.168.1.20",
            2,
            window_started_at = old_time,
        )

        current_time = datetime(
            2026,
            8,
            30,
            23,
            0,
            30
        )

        record = record_rate_limit_attempt(
            "ip",
            "192.168.1.20",
            current_time,
        )

        assert record is not None
        assert record["attempt_count"] == 3

        stored_window_start = datetime.fromisoformat(
            record["window_started_at"]
        )
        assert stored_window_start == old_time

def test_rate_limit_below_threshold_returns_false(app):
    with app.app_context():
        init_db()

        create_rate_limit(
            "ip",
            "192.168.1.20",
            4,
        )

        record = get_rate_limit(
            "ip",
            "192.168.1.20",
        )

        assert record is not None
        assert has_rate_limit_reached_threshold(record, 5) is False

def test_rate_limit_at_threshold_returns_true(app):
    with app.app_context():
        init_db()

        create_rate_limit(
            "ip",
            "192.168.1.20",
            5,
        )

        record = get_rate_limit(
            "ip",
            "192.168.1.20",
        )

        assert record is not None
        assert has_rate_limit_reached_threshold(record, 5) is True

def test_rate_limit_sets_block_until_after_threshold(app):
    with app.app_context():
        init_db()

        create_rate_limit(
            "ip",
            "192.168.1.20",
            5,
        )

        current_time = datetime(
            2026,
            8,
            30,
            23,
            0,
            0,
        )

        blocked_until = current_time + timedelta(seconds=60)

        block_rate_limit(
            "ip",
            "192.168.1.20",
            blocked_until
        )

        record = get_rate_limit(
            "ip",
            "192.168.1.20",
        )

        assert record is not None

        stored_blocked_until = datetime.fromisoformat(
            record["blocked_until"]
        )
        assert stored_blocked_until == blocked_until

def test_rate_limit_threshold_and_block_rate_limit_reached_returns_true(app):
    with app.app_context():
        init_db()

        create_rate_limit(
            "ip",
            "192.168.1.20",
            5,
        )

        record = get_rate_limit(
            "ip",
            "192.168.1.20",
        )

        assert record is not None

        current_time = datetime(
            2026,
            8,
            30,
            23,
            0,
            0
        )

        has_rate_limit_reached_threshold(record, 5)

        assert has_rate_limit_reached_threshold(record, 5) is True

def test_threshold_sets_sixty_seconds_cooldown_for_ip(app):
    with app.app_context():
        init_db()

        create_rate_limit(
            "ip_username",
            "192.168.1.20:requester_demo",
            5,
        )

        record = get_rate_limit(
            "ip_username",
            "192.168.1.20:requester_demo",
        )

        assert record is not None

        current_time = datetime(
            2026,
            8,
            30,
            23,
            0,
            0
        )

        cooldown_seconds = 60

        threshold_applied = apply_rate_limit_threshold(
            record,
            current_time,
        )

        assert threshold_applied is True

        expected_blocked_until = current_time + timedelta(
            seconds=cooldown_seconds
        )

        record = get_rate_limit(
            "ip_username",
            "192.168.1.20:requester_demo",
        )

        assert record is not None

        stored_blocked_until = datetime.fromisoformat(
            record["blocked_until"]
        )

        assert stored_blocked_until == expected_blocked_until

def test_threshold_sets_sixty_seconds_cooldown_for_ip_username(app):
    with app.app_context():
        init_db()

        create_rate_limit(
            "ip",
            "192.168.1.20",
            20,
        )

        record = get_rate_limit(
            "ip",
            "192.168.1.20",
        )

        assert record is not None

        current_time = datetime(
            2026,
            8,
            30,
            23,
            0,
            0
        )

        cooldown_seconds = 60

        threshold_applied = apply_rate_limit_threshold(
            record,
            current_time,
        )

        assert threshold_applied is True

        expected_blocked_until = current_time + timedelta(
            seconds=cooldown_seconds
        )

        record = get_rate_limit(
            "ip",
            "192.168.1.20",
        )

        assert record is not None

        stored_blocked_until = datetime.fromisoformat(
            record["blocked_until"]
        )

        assert stored_blocked_until == expected_blocked_until

def test_below_threshold_does_not_set_cooldown(app):
    with app.app_context():
        init_db()

        create_rate_limit(
            "ip",
            "192.168.1.20",
            4,
        )

        record = get_rate_limit(
            "ip",
            "192.168.1.20",
        )

        assert record is not None

        current_time = datetime(
            2026,
            8,
            30,
            23,
            0,
            0
        )

        threshold_applied = apply_rate_limit_threshold(record, current_time)

        assert threshold_applied is False

        record = get_rate_limit(
            "ip",
            "192.168.1.20",
        )

        assert record is not None
        assert record["blocked_until"] is None

def test_get_ip_and_ip_username_constraint_values():
    assert get_rate_limit_max_attempts("ip_username") == 5
    assert get_rate_limit_max_attempts("ip") == 20

def test_get_rate_limit_max_attempts_rejects_invaild_scope():
    with pytest.raises(
        ValueError,
        match="Invalid rate-limit scope",
    ):
        get_rate_limit_max_attempts("unknown")

def test_record_and_apply_rate_limit_blocks_at_threshold(app):
    with app.app_context():
        init_db()

        current_time = datetime(
            2026,
            8,
            30,
            23,
            0,
            0
        )

        old_time = current_time - timedelta(seconds=30)

        create_rate_limit(
            "ip_username",
            "192.168.1.20:requester_demo",
            4,
            window_started_at = old_time,
        )

        record = record_and_apply_rate_limit(
            "ip_username",
            "192.168.1.20:requester_demo",
            current_time,
        )

        assert record is not None
        assert record["attempt_count"] == 5
        assert record["blocked_until"] is not None

        stored_blocked_until = datetime.fromisoformat(
            record["blocked_until"]
        )

        assert stored_blocked_until == current_time + timedelta(seconds=60)

def test_login_rate_limits_ip_after_twenty_requests(app):
    with app.app_context():
        init_db()
        seed_db()

        client = app.test_client()

        for i in range(20):
            login_response = client.post(
                "/api/auth/login",
                json={
                    "username": f"requester_demo_{i}",
                    "password": "wrong-password"
                },
            )

            assert login_response.status_code == 401

        blocked_response = client.post(
            "/api/auth/login",
            json={
                "username": "requester_demo",
                "password": "wrong-password",
            },
        )

        assert blocked_response.status_code == 429

def test_login_blocks_ip_username_after_five_failures(app):
    with app.app_context():
        init_db()
        seed_db()

        client = app.test_client()

        for _ in range(5):
            login_response = client.post(
                "/api/auth/login",
                json={
                    "username": "requester_demo",
                    "password": "wrong-password",
                },
            )

            assert login_response.status_code == 401

        blocked_response = client.post(
            "/api/auth/login",
            json={
                "username": "requester_demo",
                "password": "wrong-password",
            }
        )

        assert blocked_response.status_code == 429

def test_successful_login_resets_ip_username_failures(app):
    with app.app_context():
        init_db()
        seed_db()

        client = app.test_client()

        for _ in range(3):
            login_response = client.post(
                "/api/auth/login",
                json={
                    "username": "requester_demo",
                    "password": "wrong-password",
                },
            )

            assert login_response.status_code == 401

        correct_login = client.post(
            "/api/auth/login",
            json={
                "username": "requester_demo",
                "password": "requester123",
            },
        )

        assert correct_login.status_code == 200

        pair_key = "127.0.0.1:requester_demo"

        pair_record = get_rate_limit(
            "ip_username",
            pair_key,
        )

        assert pair_record is None

def test_blocked_ip_username_rejects_correct_password_during_cooldown(app):
    with app.app_context():
        init_db()
        seed_db()

        client = app.test_client()

        for _ in range(5):
            login_reponse = client.post(
                "/api/auth/login",
                json={
                    "username": "requester_demo",
                    "password": "wrong-password",
                },
            )

            assert login_reponse.status_code == 401

        correct_login = client.post(
            "/api/auth/login",
            json={
                "username": "requester_demo",
                "password": "requester123",
            },
        )

        assert correct_login.status_code == 429

def test_expired_ip_username_block_allow_login(app):
    with app.app_context():
        init_db()
        seed_db()

        pair_key = "127.0.0.1:requester_demo"

        current_time = datetime.now()
        expired_block = current_time - timedelta(seconds=1)

        create_rate_limit(
            "ip_username",
            pair_key,
            attempt_count=5,
            window_started_at=current_time - timedelta(seconds=30),
        )

        block_rate_limit(
            "ip_username",
            pair_key,
            expired_block,
        )


        client = app.test_client()

        login_response = client.post(
            "/api/auth/login",
            json={
                "username": "requester_demo",
                "password": "requester123",
            },
        )

        assert login_response.status_code == 200

        pair_record = get_rate_limit(
            "ip_username",
            pair_key,
        )

        assert pair_record is None

def test_unknown_username_is_rate_limited_by_ip_username(app):
    with app.app_context():
        init_db()
        seed_db()

        client = app.test_client()

        for _ in range(5):
            login_response = client.post(
                "/api/auth/login",
                json={
                    "username": "unknown",
                    "password": "requester12",
                }
            )

            assert login_response.status_code == 401

        bad_login = client.post(
            "/api/auth/login",
            json={
                "username": "unknown",
                "password": "requester12",
            }
        )

        assert bad_login.status_code == 429

def test_blocked_ip_username_does_not_block_different_username(app):
    with app.app_context():
        init_db()
        seed_db()
    
        client = app.test_client()
    
        for _ in range(5):
            login_response = client.post(
                "/api/auth/login",
                json={
                    "username": "unknown",
                    "password": "requester12",
                }
            )
    
            assert login_response.status_code == 401
    
        new_username = client.post(
            "/api/auth/login",
            json={
                "username": "unknown2",
                "password": "requester12",
            }
        )
    
        assert new_username.status_code == 401

def test_blocked_ip_username_does_not_block_same_username_from_different_ip(app):
    with app.app_context():
        init_db()
        seed_db()

        client = app.test_client()

        for _ in range(5):
            login_response = client.post(
                "/api/auth/login",
                json={
                    "username": "requester_demo",
                    "password": "requester",
                },
                environ_base={"REMOTE_ADDR": "192.168.1.10"}
            )

            assert login_response.status_code == 401

        login_response_two = client.post(
            "/api/auth/login",
            json={
                "username": "requester_demo",
                "password": "requester",
            },
            environ_base={"REMOTE_ADDR": "192.168.1.10"}
        )
        
        assert login_response_two.status_code == 429

        new_login = client.post(
            "/api/auth/login",
            json={
                "username": "requester_demo",
                "password": "requester",
            },
             environ_base={"REMOTE_ADDR": "192.168.1.11"}
        )

        assert new_login.status_code == 401
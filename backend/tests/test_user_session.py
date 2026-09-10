from app.db import get_db, init_db
from app.seed import seed_db
from datetime import datetime, timedelta
from app.user_sessions import create_user_session, get_user_session, has_user_session_expired, is_user_session_active, revoke_user_session, validate_user_session

def test_create_user_sessions_stores_active_session(app):
    with app.app_context():
        init_db()
        seed_db()

        db = get_db()

        requester = db.execute(
            "SELECT id FROM users WHERE username = ?",
            ("requester_demo",)
        ).fetchone()

        session_id =  "test-session-123"

        create_user_session(
            requester["id"],
            session_id,
        )

        session_info = db.execute(
            """
            SELECT session_id, user_id, revoked_at
            FROM user_sessions
            WHERE user_id = ?
            """,
            (requester["id"],)
        ).fetchone()

        assert session_info is not None
        assert session_info["session_id"] == session_id
        assert session_info["user_id"] == requester["id"]
        assert session_info["revoked_at"] is None

def test_get_user_session_returns_matching_session(app):
    with app.app_context():
        init_db()
        seed_db()

        db = get_db()

        requester = db.execute(
            "SELECT id FROM users WHERE username = ?",
            ("requester_demo",)
        ).fetchone()

        session_id = "test-session-123"

        create_user_session(
            requester["id"], 
            "test-session-123"
            )

        session_info = get_user_session(session_id)
        
        assert session_info is not None
        assert session_info["session_id"] == session_id
        assert session_info["user_id"] == requester["id"]
        assert session_info["revoked_at"] is None

def test_get_user_session_returns_none_for_unknown_session(app):
    with app.app_context():
        init_db()

        session_info = get_user_session("does-not-exist")
        
        assert session_info is None

def test_revoke_user_session_sets_revoked_at(app):
    with app.app_context():
        init_db()
        seed_db()

        db = get_db()

        requester = db.execute(
            "SELECT id FROM users WHERE username = ?",
            ("requester_demo",)
        ).fetchone()

        session_id = "test-session-123"

        create_user_session(
            requester["id"],
            "test-session-123",
        )

        session_info = get_user_session(session_id)

        assert session_info["revoked_at"] is None

        revoke_user_session(session_id)

        revoked_session = get_user_session(session_id)

        assert revoked_session["revoked_at"] is not None

def test_active_user_session_is_valid(app):
    with app.app_context():
        init_db()
        seed_db()

        db = get_db()

        requester = db.execute(
            "SELECT id FROM users WHERE username = ?",
            ("requester_demo",)
        ).fetchone()
        
        session_id = "test-session-123"
        
        create_user_session(
            requester["id"],
            session_id,
        )

        is_active = is_user_session_active(session_id)

        assert is_active is True

def test_revoked_user_session_is_not_active(app):
    with app.app_context():
        init_db()
        seed_db()

        db = get_db()

        requester = db.execute(
            "SELECT id FROM users WHERE username = ?",
            ("requester_demo",)
        ).fetchone()
        
        session_id = "test-session-123"
        
        create_user_session(
            requester["id"],
            session_id,
        )

        revoke_user_session(session_id)

        is_active = is_user_session_active(session_id)

        assert is_active is False

def test_unknown_user_session_is_not_active(app):
    with app.app_context():
        init_db()

        is_active = is_user_session_active("does-not-exist")

        assert is_active is False

def test_successful_login_creates_active_user_session(app):
    with app.app_context():
        init_db()
        seed_db()

        client = app.test_client()

        login_response = client.post(
            "/api/auth/login",
            json={
                "username": "requester_demo",
                "password": "requester123"
            }
        )

        assert login_response.status_code == 200

        with client.session_transaction() as flask_session:
            session_id = flask_session.get("session_id")
            user_id = flask_session.get("user_id")

            assert session_id is not None
            assert user_id is not None

        session_record = get_user_session(session_id)

        assert session_record is not None
        assert session_record["session_id"] == session_id
        assert session_record["user_id"] == user_id
        assert session_record["revoked_at"] is None

def test_logout_revokes_user_session(app):
    with app.app_context():
        init_db()
        seed_db()

        client = app.test_client()
        
        login_response = client.post(
            "/api/auth/login",
            json={
                "username": "requester_demo",
                "password": "requester123"
            }
        )
        
        assert login_response.status_code == 200
        
        with client.session_transaction() as flask_session:
            session_id = flask_session.get("session_id")
        
            assert session_id is not None

        current_session = get_user_session(session_id)

        assert current_session is not None
        assert current_session["revoked_at"] is None

        logout_response = client.post("/api/auth/logout")

        assert logout_response.status_code == 200

        revoked_session = get_user_session(session_id)

        assert revoked_session is not None
        assert revoked_session["revoked_at"] is not None

def test_user_session_is_invalid_for_different_user(app):
    with app.app_context():
        init_db()
        seed_db()

        db = get_db()
        
        requester = db.execute(
            "SELECT id FROM users WHERE username = ?",
            ("requester_demo",)
        ).fetchone()
        
        resolver = db.execute(
            "SELECT id FROM users WHERE username = ?",
            ("resolver_demo",)
        ).fetchone()

        session_id = "test-session-123"

        create_user_session(
            requester["id"],
            session_id,
        )

        is_valid = validate_user_session(
            resolver["id"],
            session_id,
        )

        assert is_valid is False

def test_user_session_older_than_four_hours_is_invalid(app):
    with app.app_context():
        init_db()
        seed_db()

        db = get_db()

        user = db.execute(
            "SELECT id FROM users WHERE username = ?",
            ("requester_demo",),
        ).fetchone()

        session_id = "expired-session-test"

        create_user_session(user["id"], session_id)

        created_at = datetime.now() - timedelta(hours=5)

        db.execute(
            """
            UPDATE user_sessions
            SET created_at = ?
            WHERE session_id = ?
            """,
            (
                created_at.isoformat(sep=" "),
                session_id,
            ),
        )

        db.commit()

        is_valid = validate_user_session(
            user["id"],
            session_id,
        )

        assert is_valid is False

def test_user_session_before_max_lifetime_is_not_expired(app):
    with app.app_context():

        current_time = datetime.now()

        created_at = current_time - timedelta(
            hours=3,
            minutes=59,
            seconds=59,
        )

        session_info = {
            "created_at": created_at.isoformat(sep=" ")
        }

        is_expired = has_user_session_expired(
            session_info,
            current_time,
        )

        assert is_expired is False

def test_user_session_at_max_lifetime_is_expired(app):
    with app.app_context():
        current_time = datetime.now()
        
        created_at = current_time - timedelta(hours=4)
        
        session_info = {
            "created_at": created_at.isoformat(sep=" ")
        }
        
        is_expired = has_user_session_expired(
            session_info,
            current_time,
        )
        
        assert is_expired is True

def test_expired_session_cannot_access_protected_ticket_route(app):
    with app.app_context():
        init_db()
        seed_db()

        db = get_db()

        client = app.test_client()

        user = client.post(
            "/api/auth/login",
            json={
                "username": "requester_demo",
                "password": "requester123",
            }
        )

        with client.session_transaction() as flask_session:
            session_id = flask_session["session_id"]
    

        created_at = datetime.now() - timedelta(hours=5)

        db.execute(
            """
            UPDATE user_sessions
            SET created_at = ?
            WHERE session_id = ?
            """,
            (
                created_at.isoformat(sep=" "),
                session_id,
                ),
        )

        db.commit()

        response = client.get("/api/tickets")

        assert response.status_code == 401
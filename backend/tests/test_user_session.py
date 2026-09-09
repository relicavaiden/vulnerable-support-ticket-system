from app.db import get_db, init_db
from app.seed import seed_db
from app.user_sessions import create_user_session, get_user_session, is_user_session_active, revoke_user_session, validate_user_session

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
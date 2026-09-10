import pytest

from app.db import get_db, init_db
from app.seed import seed_db
from app.user_sessions import create_user_session, get_user_session

def test_logged_out_session_cannot_access_authenticated_route(app):
    with app.app_context():
        init_db()
        seed_db()

        client = app.test_client()

        login_response = client.post(
            "/api/auth/login",
            json={
                "username": "requester_demo",
                "password": "requester123",
            }
        )

        assert login_response.status_code == 200

        authenticated_response = client.get("/api/auth/me")
        assert authenticated_response.status_code == 200

        logout_response = client.post(
            "/api/auth/logout"
        )

        assert logout_response.status_code == 200

        after_logout_response = client.get(
            "/api/auth/me"
        )

        assert after_logout_response.status_code == 401

def test_logout_clears_session_cookie(app):
    with app.app_context():
        init_db()
        seed_db()

        client = app.test_client()

        login_response = client.post(
            "/api/auth/login",
            json={
                "username": "requester_demo",
                "password": "requester123",
            }
        )

        login_cookie = login_response.headers.get("Set-Cookie")

        assert login_response.status_code == 200

        logout_response = client.post(
            "/api/auth/logout",
        )

        logout_cookie = logout_response.headers.get("Set-Cookie")

        assert logout_cookie is not None
        assert "session=;" in logout_cookie
        assert "Max-Age=0" in logout_cookie
        assert "Expires=Thu, 01 Jan 1970 00:00:00 GMT" in logout_cookie

        assert "Secure" in logout_cookie
        assert "HttpOnly" in logout_cookie
        assert "SameSite=Lax" in logout_cookie

@pytest.mark.skip(
        reason="V1 session replay baseline; V2 revokes and validates server-side sessions"
)
def test_logged_out_session_cookie_can_be_replayed(app):
    with app.app_context():
        init_db()
        seed_db()

        client = app.test_client()

        login_response = client.post(
            "/api/auth/login",
            json={
                "username": "requester_demo",
                "password": "requester123",
            }
        )

        old_cookie = client.get_cookie("session")

        assert old_cookie is not None
        assert login_response.status_code == 200

        authenticated_response = client.get("/api/auth/me")

        assert authenticated_response.status_code == 200

        after_logout_response = client.post(
            "/api/auth/logout",
        )

        assert client.get_cookie("session") is None
        assert after_logout_response.status_code == 200

        new_client = app.test_client()

        new_client.set_cookie(
            "session",
            old_cookie.decoded_value,
            domain=old_cookie.domain,
            path=old_cookie.path,
        )

        replayed_cookie = new_client.get_cookie(
            "session",
            domain=old_cookie.domain,
            path=old_cookie.path,
        )

        assert replayed_cookie is not None

        replay_response = new_client.get("/api/auth/me")

        assert replay_response.status_code == 200

        data = replay_response.get_json()

        assert data["user"]["username"] == "requester_demo"

def test_logged_out_session_cookie_cannot_be_replayed(app):
    with app.app_context():
        init_db()
        seed_db()
    
        client = app.test_client()
    
        login_response = client.post(
            "/api/auth/login",
            json={
                "username": "requester_demo",
                "password": "requester123",
            }
        )
    
        old_cookie = client.get_cookie("session")
    
        assert old_cookie is not None
        assert login_response.status_code == 200
    
        authenticated_response = client.get("/api/auth/me")
    
        assert authenticated_response.status_code == 200
    
        after_logout_response = client.post(
            "/api/auth/logout",
        )
    
        assert client.get_cookie("session") is None
        assert after_logout_response.status_code == 200
    
        new_client = app.test_client()
    
        new_client.set_cookie(
            "session",
            old_cookie.decoded_value,
            domain=old_cookie.domain,
            path=old_cookie.path,
        )
    
        replayed_cookie = new_client.get_cookie(
            "session",
            domain=old_cookie.domain,
            path=old_cookie.path,
        )
    
        assert replayed_cookie is not None
    
        replay_response = new_client.get("/api/auth/me")
    
        assert replay_response.status_code == 401
    
        data = replay_response.get_json()
    
        assert data["error"] == "Not authenticated"

def test_revoked_session_cookie_cannot_access_ticket_routes(app):
    with app.app_context():
        init_db()
        seed_db()

        client = app.test_client()

        login_response = client.post(
            "/api/auth/login",
            json={
                "username": "requester_demo",
                "password": "requester123",
            }
        )

        pre_logout_cookie = client.get_cookie("session")
        
        assert pre_logout_cookie is not None
        assert login_response.status_code == 200

        logout_response = client.post("/api/auth/logout")

        assert logout_response.status_code == 200

        new_client = app.test_client()
        
        new_client.set_cookie(
            "session",
            pre_logout_cookie.decoded_value,
            domain=pre_logout_cookie.domain,
            path=pre_logout_cookie.path,
        )

        ticket_test = new_client.get("/api/tickets")

        assert ticket_test.status_code == 401

        data = ticket_test.get_json()

        assert data["error"] == "Not authenticated"

def test_session_lifetime_configuration(app):
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

        with client.session_transaction() as flask_session:
            print(flask_session.permanent)

        print(app.config["PERMANENT_SESSION_LIFETIME"])
        print(app.config["SESSION_REFRESH_EACH_REQUEST"])

        set_cookie = login_response.headers.get("Set-Cookie")

        print(set_cookie)
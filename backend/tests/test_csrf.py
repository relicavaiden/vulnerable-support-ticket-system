import pytest

from app.db import get_db, init_db
from app.seed import seed_db

def test_authenticated_ticket_creation_accepts_request_without_csrf_token(app):
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

        response = client.post(
            "/api/tickets",
            json={
                "title": "Checking CSRF token",
                "description": "Checking what the response is with no CSRF token",
                "category": "account_access",
            },
        )

        print(response.status_code)
        print(response.get_json())

def test_authenticated_ticket_creation_with_form_data_without_csrf_token(app):
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

        response = client.post(
            "/api/tickets",
            data={
                "title": "CSRF form test",
                "description": "Testing form submission.",
                "category": "account_access",
            },
        )

        print(response.status_code)
        print(response.get_json())

@pytest.mark.skip(
        reason="V1 cookie baseline; V2 hardens Secure and Samesite attributes"
)
def test_session_cookie_security_attributes(app):
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


        assert (app.config["SESSION_COOKIE_HTTPONLY"]) is True
        assert (app.config["SESSION_COOKIE_SECURE"]) is False
        assert (app.config["SESSION_COOKIE_SAMESITE"]) is None

        set_cookie = login_response.headers.get("Set-Cookie")

        assert set_cookie is not None
        assert "HttpOnly" in set_cookie
        assert "Secure" not in set_cookie
        assert "SameSite" not in set_cookie

def test_session_cookie_uses_secure_attributes(app):
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

        assert app.config["SESSION_COOKIE_HTTPONLY"] is True
        assert app.config["SESSION_COOKIE_SECURE"] is True
        assert app.config["SESSION_COOKIE_SAMESITE"] == "Lax"

        set_cookie = login_response.headers.get("Set-Cookie")

        assert set_cookie is not None
        assert "HttpOnly" in set_cookie
        assert "Secure" in set_cookie
        assert "SameSite=Lax" in set_cookie
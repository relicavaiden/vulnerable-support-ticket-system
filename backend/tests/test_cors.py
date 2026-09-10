from app.db import get_db, init_db
from app.seed import seed_db

def test_authenticated_request_from_untrusted_origin_cors_headers(app):
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

        response = client.get(
            "/api/tickets",
            headers={
                "Origin": "https://evil.example",
            }
        )

        assert response is not None

        assert response.status_code == 200
        assert response.headers.get("Access-Control-Allow-Origin") is None
        assert response.headers.get("Access-Control-Allow-Credentials") is None

def test_authenticated_request_from_trusted_origin_cors_headers(app):
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

        response = client.get(
            "/api/tickets",
            headers={
                "Origin": "http://localhost:3000",
            }
        )

        assert response is not None

        print(response.status_code)
        print(response.headers.get("Access-Control-Allow-Origin"))
        print(response.headers.get("Access-Control-Allow-Credentials"))
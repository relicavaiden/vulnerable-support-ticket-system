from app.db import get_db, init_db
from app.seed import seed_db

def test_invalid_ticket_request_does_not_expose_internal_error_details(app):
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

        response = client.post(
            "/api/tickets",
            json={
                "body": "This should be the title",
                "title": "This should be the body",
                "category": "software",
                "status": "closed"
            }
        )

        assert response.status_code == 400

        data = response.get_json()

        assert data is not None
        assert data["error"] == "Description is required"

def test_invalid_title_creation_does_not_expose_internal_error_details(app):
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

        response = client.post(
            "/api/tickets",
            json={
                "title": ["This", "is", "not", "a", "string"],
                "description": "This should be the body",
                "category": "software",
                "status": "closed"
            }
        )

        assert response.status_code == 400

        data = response.get_json()

        assert data is not None
        assert data["error"] == "Title is required"

def test_malformed_json_does_not_expose_internal_error_details(app):
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
            data='{title": "Broken JSON",',
            content_type="application/json",
        )

        assert response.status_code == 400

        response_text = response.get_data(as_text=True)

        assert "Bad Request" in response_text
        assert "Traceback" not in response_text
        assert "sqlite3" not in response_text
        assert "File \"" not in response_text

        print(app.config["DEBUG"])
        print(app.config["TESTING"])
        print(app.config["PROPAGATE_EXCEPTIONS"])


from app.db import get_db, init_db
from app.seed import seed_db

def test_ticket_description_stores_html_payload_as_data(app):
    with app.app_context():
        init_db()
        seed_db()

        db = get_db()

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
                "title": "XSS attempt",
                "description": '<script>alert("xss-test")</script>',
                "status": "open",
                "category": "account_access",
            }
        )

        assert response.status_code == 201

        ticket = db.execute(
            """
            SELECT description
            FROM tickets
            WHERE title = ?
            """,
            ("XSS attempt",)
        ).fetchone()

        assert ticket is not None
        assert ticket["description"] == '<script>alert("xss-test")</script>'
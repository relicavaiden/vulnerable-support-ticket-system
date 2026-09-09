import pytest

from app.db import get_db, init_db
from app.seed import seed_db

def test_login_username_is_not_vulnerable_to_sql_injection(app):
    with app.app_context():
        init_db()
        seed_db()

        client = app.test_client()

        sql_login = client.post(
            "/api/auth/login",
            json={
                "username": "' OR 1=1 --",
                "password": "testing",
            }
        )

        assert sql_login.status_code == 401

        data = sql_login.get_json()

        assert data["error"] == "Invalid username or password"

def test_ticket_detail_rejects_non_integer_id(app):
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

        response = client.get("/api/tickets/1' OR '1'='1")
        response_two = client.get("/api/tickets/1 OR 1=1")

        assert response.status_code == 404
        assert response_two.status_code == 404

def test_note_body_is_treated_as_data_not_sql(app):
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

        client = app.test_client()

        login_response = client.post(
            "/api/auth/login",
            json={
                "username": "requester_demo",
                "password": "requester123",
            },
        )

        assert login_response.status_code == 200

        ticket_cursor = db.execute(
            """
            INSERT INTO tickets (
            title,
            description,
            status,
            category,
            requester_id,
            assigned_resolver_id
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                "Test ticket for SQL",
                "This is a test ticket",
                "open",
                "account_access",
                requester["id"],
                resolver["id"],
            )
        )
        
        ticket_id = ticket_cursor.lastrowid
        
        db.commit()

        response = client.post(
            f"/api/tickets/{ticket_id}/notes",
            json={
                "body": "'); DROP TABLE users; --"
            },
        )

        assert response.status_code == 201

        note = db.execute(
            """
            SELECT ticket_id, author_id, note_type, body
            FROM ticket_notes
            WHERE ticket_id = ?
            """,
            (ticket_id,)
        ).fetchone()

        assert note is not None
        assert note["body"] == "'); DROP TABLE users; --"

        users = db.execute(
            "SELECT id FROM users"
        ).fetchall()

        assert len(users) > 0

def test_ticket_title_is_treated_as_data_not_sql(app):
    with app.app_context():
        init_db()
        seed_db()

        db = get_db()
        
        client = app.test_client()

        login_response = client.post(
            "/api/auth/login",
            json={
                "username": "requester_demo",
                "password": "requester123",
            },
        )

        assert login_response.status_code == 200
        
        response = client.post(
            "/api/tickets",
            json={
                "title": "'); DROP TABLE users; --",
                "description": "Trying to assign this to another reolver.",
                "category": "account_access",
            },
        )

        data = response.get_json()

        assert data is not None
        assert response.status_code == 201
        users = db.execute(
            "SELECT id FROM users"
        ).fetchall()
        
        assert len(users) > 0

        


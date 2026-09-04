from app.db import get_db, init_db
from app.seed import seed_db
from werkzeug.security import generate_password_hash

def test_requester_cannot_access_another_requesters_ticket_by_id(app):
    with app.app_context():
        init_db()
        seed_db()

        db = get_db()


        resolver = db.execute(
            "SELECT id FROM users WHERE username = ?",
            ("resolver_demo",)
        ).fetchone()

        requester_a = db.execute(
            """
            INSERT INTO users (username, password_hash, role, is_seeded)
            VALUES (?, ?, ?, ?)
            """,
            ("requester_a", generate_password_hash("passwordA"), "requester", 0)
        )

        requester_b = db.execute(
            """
            INSERT INTO users (username, password_hash, role, is_seeded)
            VALUES (?, ?, ?, ?)
            """,
            ("requester_b", generate_password_hash("passwordB"), "requester", 0)
        )

        requester_b_id = requester_b.lastrowid

        ticket_cursor= db.execute(
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
                "Assigned to requester_b",
                "This ticket belongs to requester_b",
                "open",
                "account_access",
                requester_b_id,
                resolver["id"],
            )
        )

        ticket_id = ticket_cursor.lastrowid

        db.commit()

        client = app.test_client()

        requester_a_login = client.post(
            "/api/auth/login",
            json={
                "username": "requester_a",
                "password": "passwordA",
            }
        )

        assert requester_a_login.status_code == 200

        record = client.get(f"/api/tickets/{ticket_id}")

        assert record.status_code == 403, record.get_data(as_text=True)

        data = record.get_json()

        assert data["error"] == "Forbidden"

def test_resolver_cannot_access_another_resolvers_ticket_by_id(app):
    with app.app_context():
        init_db()
        seed_db()

        db = get_db()

        requester = db.execute(
            "SELECT id FROM users WHERE username = ?",
            ("requester_demo",)
        ).fetchone()

        resolver_a = db.execute(
            """
            INSERT INTO users (username, password_hash, role, is_seeded)
            VALUES (?, ?, ?, ?)
            """,
            ("resolver_a", generate_password_hash("passwordA"), "resolver", 0)
        )
        
        resolver_b = db.execute(
            """
            INSERT INTO users (username, password_hash, role, is_seeded)
            VALUES (?, ?, ?, ?)
            """,
            ("resolver_b", generate_password_hash("passwordB"), "resolver", 0)
        )
        
        resolver_b_id = resolver_b.lastrowid
        
        ticket_cursor= db.execute(
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
                "Assigned to resolver_b",
                "This ticket belongs to resolver_b",
                "open",
                "account_access",
                requester["id"],
                resolver_b_id,
            )
        )
        
        ticket_id = ticket_cursor.lastrowid
        
        db.commit()
        
        client = app.test_client()
        
        resolver_a_login = client.post(
            "/api/auth/login",
            json={
                "username": "resolver_a",
                "password": "passwordA",
            }
        )
        
        assert resolver_a_login.status_code == 200
        
        record = client.get(f"/api/tickets/{ticket_id}")
        
        assert record.status_code == 403, record.get_data(as_text=True)
        
        data = record.get_json()
        
        assert data["error"] == "Forbidden"
from app import create_app
from app.db import get_db, init_db
from app.seed import seed_db

def test_get_tickets_without_login_returns_401(tmp_path):
    app = create_app()
    database_path = tmp_path / "tickets.db"
    app.config["DATABASE"] = str(database_path)

    with app.app_context():
        init_db()

    client = app.test_client()

    response = client.get("/api/tickets")

    assert response.status_code == 401

    data = response.get_json()

    assert data["error"] == "Not authenticated"

def test_get_tickets_with_logged_in_requester_returns_ticket_list(tmp_path):
    app = create_app()
    database_path = tmp_path / "tickets.db"
    app.config["DATABASE"] = str(database_path)
    app.config["TESTING"] = True

    with app.app_context():
        init_db()
        seed_db()

    client = app.test_client()

    login_response = client.post(
        "/api/auth/login",
        json={
            "username": "requester_demo",
            "password": "requester123",
        },
    )

    assert login_response.status_code == 200, login_response.get_data(as_text=True)

    response = client.get("/api/tickets")

    print(response.get_json())

    assert response.status_code == 200, response.get_data(as_text=True)

    data = response.get_json()

    assert "tickets" in data
    assert isinstance(data["tickets"], list)

def test_logged_in_requester_can_create_ticket(tmp_path):
    app = create_app()
    database_path = tmp_path / "tickets.db"
    app.config["DATABASE"] = str(database_path)
    app.config["TESTING"] = True

    with app.app_context():
        init_db()
        seed_db()

        db = get_db()

        resolver = db.execute(
            "SELECT id, username, role FROM users WHERE role = ?",
            ("resolver",)
        ).fetchone()

        assert resolver is not None

    client = app.test_client()

    login_response = client.post(
        "/api/auth/login",
        json={
            "username": "requester_demo",
            "password": "requester123",
        },
    )

    assert login_response.status_code == 200, login_response.get_data(as_text=True)

    response = client.post(
        "/api/tickets",
        json={
            "title": "Cannot access account",
            "description": "I am unable to log into my account.",
            "category": "account_access",
        },
    )

    assert response.status_code == 201, response.get_data(as_text=True)

    data = response.get_json()

    assert data["ticket"]["title"] == "Cannot access account"
    assert data["ticket"]["description"] == "I am unable to log into my account."
    assert data["ticket"]["category"] == "account_access"
    assert data["ticket"]["status"] == "open"

    with app.app_context():
        db = get_db()

        requester = db.execute(
            "SELECT id FROM users WHERE username = ?",
            ("requester_demo",)
        ).fetchone()

        ticket = db.execute(
            """
            SELECT title, description, category, status, requester_id
            FROM tickets
            WHERE title = ?
            """,
            ("Cannot access account",)
        ).fetchone()

        assert ticket is not None
        assert ticket["requester_id"] == requester["id"]

def test_logged_in_requester_can_list_their_created_tickets(tmp_path):
    app = create_app()
    database_path = tmp_path / "tickets.db"
    app.config["DATABASE"] = str(database_path)
    app.config["TESTING"] = True

    with app.app_context():
        init_db()
        seed_db()
        
    client = app.test_client()

    login_response = client.post(
        "/api/auth/login",
        json={
            "username": "requester_demo",
            "password": "requester123",
        },
    )

    assert login_response.status_code == 200, login_response.get_data(as_text=True)

    create_response = client.post(
        "/api/tickets",
        json={
            "title": "Cannot access account",
            "description": "I am unable to log into my account.",
            "category": "account_access",
        },
    )

    assert create_response.status_code == 201, create_response.get_data(as_text=True)

    response = client.get("/api/tickets")

    assert response.status_code == 200, response.get_data(as_text=True)

    data = response.get_json()

    assert "tickets" in data
    assert len(data["tickets"]) == 1

    ticket = data["tickets"][0]

    assert ticket["title"] == "Cannot access account"
    assert ticket["description"] == "I am unable to log into my account."
    assert ticket["category"] == "account_access"
    assert ticket["status"] == "open"

def test_requester_only_lists_their_own_tickets(tmp_path):
    app = create_app()
    database_path = tmp_path / "tickets.db"
    app.config["DATABASE"] = str(database_path)
    app.config["TESTING"] = True

    with app.app_context():
        init_db()
        seed_db()

        db = get_db()

        requester = db.execute(
            "SELECT id FROM users WHERE username = ?",
            ("requester_demo",)
        ).fetchone()

        resolver = db.execute(
            "SELECT id FROM users WHERE role = ?",
            ("resolver",)
        ).fetchone()

        other_requester_cursor = db.execute(
            """
            INSERT INTO users (username, password_hash, role, is_seeded)
            VALUES (?, ?, ?, ?)
            """,
            ("other_requester", "not_used", "requester", 0)
        )

        other_requester_id = other_requester_cursor.lastrowid

        db.execute(
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
                "My ticket",
                "This belongs to requester_demo",
                "open",
                "account_access",
                requester["id"],
                resolver["id"],
            )
        )

        db.commit()

    client = app.test_client()

    login_response = client.post(
        "/api/auth/login",
        json={
            "username": "requester_demo",
            "password": "requester123",
        },
    )

    assert login_response.status_code == 200, login_response.get_data(as_text=True)

    response = client.get("/api/tickets")

    assert response.status_code == 200, response.get_data(as_text=True)

    data = response.get_json()

    assert len(data["tickets"]) == 1
    assert data["tickets"][0]["title"] == "My ticket"

def test_resolver_cannot_create_ticket(tmp_path):
    app = create_app()
    database_path = tmp_path / "tickets.db"
    app.config["DATABASE"] = str(database_path)
    app.config["TESTING"] = True

    with app.app_context():
        init_db()
        seed_db()

    client = app.test_client()

    login_response = client.post(
        ("/api/auth/login"),
        json={
            "username": "resolver_demo",
            "password": "resolver123",
        },
    )

    assert login_response.status_code == 200, login_response.get_data(as_text=True)

    response = client.post(
        "/api/tickets",
        json={
            "title": "Resolver should not create this",
            "description": "Resolvers should not create requester tickets.",
            "category": "account_access",
        },
    )

    assert response.status_code == 403, response.get_data(as_text=True)

    data = response.get_json()

    assert data["error"] == "Forbidden"

    with app.app_context():
        db = get_db()

        tickets = db.execute(
            "SELECT id FROM tickets"
        ).fetchall()

        assert len(tickets) == 0

def test_resolver_lists_assigned_tickets(tmp_path):
    app = create_app()
    database_path = tmp_path / "tickets.db"
    app.config["DATABASE"] = str(database_path)
    app.config["TESTING"] = True

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

        db.execute(
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
                "Assigned resolver ticket",
                "This ticket is assigned to resolver_demo.",
                "open",
                "account_access",
                requester["id"],
                resolver["id"],
            )
        )

        db.commit()

    client = app.test_client()

    login_response = client.post(
        "/api/auth/login",
        json={
            "username": "resolver_demo",
            "password": "resolver123",
        },
    )

    assert login_response.status_code == 200, login_response.get_data(as_text=True)

    response = client.get("/api/tickets")

    assert response.status_code == 200, response.get_data(as_text=True)

    data = response.get_json()

    assert "tickets" in data

    assert len(data["tickets"]) == 1

    ticket = data["tickets"][0]

    assert ticket["title"] == "Assigned resolver ticket"
    assert ticket["description"] == "This ticket is assigned to resolver_demo."
    assert ticket["category"] == "account_access"
    assert ticket["status"] == "open"

def test_resolver_only_lists_their_assigned_tickets(tmp_path):
    app = create_app()
    database_path = tmp_path / "tickets.db"
    app.config["DATABASE"] = str(database_path)
    app.config["TESTING"] = True

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

        other_resolver_cursor = db.execute(
            """
            INSERT INTO users (username, password_hash, role, is_seeded)
            VALUES (?, ?, ?, ?)
            """,
            ("other_resolver", "not-used", "resolver", 0)
        )

        other_resolver_id = other_resolver_cursor.lastrowid

        db.execute(
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
                "Assigned to resolver demo",
                "This ticket belongs to resolver_demo.",
                "open",
                "account_access",
                requester["id"],
                resolver["id"],
            )
        )

        db.execute(
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
                "Assigned to another reolver",
                "This ticket belongs to another resolver,",
                "open",
                "account_access",
                requester["id"],
                other_resolver_id,
            )
        )

        db.commit()

    client = app.test_client()

    login_response = client.post(
        "/api/auth/login",
        json={
            "username": "resolver_demo",
            "password": "resolver123",
        },
    )

    assert login_response.status_code == 200, login_response.get_data(as_text=True)

    response = client.get("/api/tickets")

    assert response.status_code == 200, response.get_data(as_text=True)

    data = response.get_json()

    assert "tickets" in data
    assert len(data["tickets"]) == 1

    ticket = data["tickets"][0]

    assert ticket["title"] == "Assigned to resolver demo"
    assert ticket["description"] == "This ticket belongs to resolver_demo."
    assert ticket["category"] == "account_access"
    assert ticket["status"] == "open"

def test_create_ticket_uses_session_user_not_request_body_requester_id(tmp_path):
    app = create_app()
    database_path = tmp_path / "tickets.db"
    app.config["DATABASE"] = str(database_path)
    app.config["TESTING"] = True

    with app.app_context():
        init_db()
        seed_db()

        db = get_db()

        requester = db.execute(
            "SELECT id FROM users WHERE username = ?",
            ("requester_demo",)
        ).fetchone()
    
        other_resquester_cursor = db.execute(
            """
            INSERT INTO users (username, password_hash, role, is_seeded)
            VALUES(?, ?, ?, ?)
            """,
            ("other_requester", "not-used", "requester", 0)
        )
    
        other_requester_id = other_resquester_cursor.lastrowid

        db.commit()

    client = app.test_client()

    login_response = client.post(
        "/api/auth/login",
        json={
            "username": "requester_demo",
            "password": "requester123",
        },
    )

    assert login_response.status_code == 200, login_response.get_data(as_text=True)

    response = client.post(
        "/api/tickets",
        json={
            "title": "Spoofed requester ticket",
            "description": "Trying to create this as another requester.",
            "category": "account_access",
            "requester_id": other_requester_id,
        },
    )

    assert response.status_code == 201, response.get_data(as_text=True)

    with app.app_context():
        db = get_db()

        ticket = db.execute(
            """
            SELECT requester_id
            FROM tickets
            WHERE title = ?
            """,
            ("Spoofed requester ticket",)
        ).fetchone()

        assert ticket is not None
        assert ticket["requester_id"] == requester["id"]
        assert ticket["requester_id"] != other_requester_id

def test_create_ticket_uses_backend_assigned_resolver_not_request_body(tmp_path):
    app = create_app()
    database_path = tmp_path / "tickets.db"
    app.config["DATABASE"] = str(database_path)
    app.config["TESTING"] = True

    with app.app_context():
        init_db()
        seed_db()

        db = get_db()

        resolver = db.execute(
            "SELECT id FROM users WHERE username = ?",
            ("resolver_demo",)
        ).fetchone()

        other_resolver_cursor = db.execute(
            """
            INSERT INTO users (username, password_hash, role, is_seeded)
            VALUES (?, ?, ?, ?)
            """,
            ("other_resolver_id", "not-used", "resolver", 0)
        )

        other_resolver_id = other_resolver_cursor.lastrowid

        db.commit()

    client = app.test_client()

    login_response = client.post(
        "/api/auth/login",
        json={
            "username": "requester_demo",
            "password": "requester123"
        }
    )

    assert login_response.status_code == 200, login_response.get_data(as_text=True)

    response = client.post(
        "/api/tickets",
        json={
            "title": "Spoofed resolver ticket",
            "description": "Trying to assign this to another reolver.",
            "category": "account_access",
            "assigned_resolver_id": other_resolver_id,
        },
    )

    assert response.status_code == 201, response.get_data(as_text=True)

    with app.app_context():
        db = get_db()

        ticket = db.execute(
            """
            SELECT assigned_resolver_id
            FROM tickets
            WHERE title = ?
            """,
            ("Spoofed resolver ticket",)
        ).fetchone()

        assert ticket is not None
        assert ticket["assigned_resolver_id"] == resolver["id"]
        assert ticket["assigned_resolver_id"] != other_resolver_id

def test_unauthenticated_user_cannot_view_ticket_detail(tmp_path):
    app = create_app()
    database_path = tmp_path / "tickets.db"
    app.config["DATABASE"] = str(database_path)
    app.config["TESTING"] = True

    with app.app_context():
        init_db()
        seed_db()

    client = app.test_client()

    response = client.get("/api/tickets/1")

    assert response.status_code == 401, response.get_data(as_text=True)

    data = response.get_json()

    assert data["error"] == "Not authenticated"

def test_requester_can_view_own_ticket_detail(tmp_path):
    app = create_app()
    database_path = tmp_path / "tickets.db"
    app.config["DATABASE"] = str(database_path)
    app.config["TESTING"] = True

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
                "Own ticket detail",
                "Requester should be able to view this ticket.",
                "open",
                "account_access",
                requester["id"],
                resolver["id"],
            )
        )

        ticket_id = ticket_cursor.lastrowid

        db.commit()

    client = app.test_client()

    login_response = client.post(
        "/api/auth/login",
        json={
            "username": "requester_demo",
            "password": "requester123",
        },
    )

    assert login_response.status_code == 200, login_response.get_data(as_text=True)

    response = client.get(f"/api/tickets/{ticket_id}")

    assert response.status_code == 200, response.get_data(as_text=True)

    data = response.get_json()

    assert "ticket" in data

    ticket = data["ticket"]

    assert ticket["id"] == ticket_id
    assert ticket["title"] == "Own ticket detail"
    assert ticket["description"] == "Requester should be able to view this ticket."
    assert ticket["status"] == "open"
    assert ticket["category"] == "account_access"

def test_requester_cannot_view_another_requesters_ticket_detail(tmp_path):
    app = create_app()
    database_path = tmp_path / "tickets.db"
    app.config["DATABASE"] = str(database_path)
    app.config["TESTING"] = True

    with app.app_context():
        init_db()
        seed_db()

        db = get_db()

        resolver = db.execute(
            "SELECT id FROM users WHERE username = ?",
            ("resolver_demo",)
        ).fetchone()

        other_requester_cursor = db.execute(
            """
            INSERT INTO users (username, password_hash, role, is_seeded)
            VALUES (?, ?, ?, ?)
            """,
            ("other_requester", "not-used", "requester", 0)
        )

        other_requester_id = other_requester_cursor.lastrowid

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
                "Other requester detail",
                "requester_demo should not be able to view this ticket.",
                "open",
                "account_access",
                other_requester_id,
                resolver["id"]
            )
        )

        ticket_id = ticket_cursor.lastrowid

        db.commit()

        client = app.test_client()

        login_response = client.post(
            "/api/auth/login",
            json={
                "username": "requester_demo",
                "password": "requester123",
            },
        )

        assert login_response.status_code == 200, login_response.get_data(as_text=True)

        response = client.get(f"/api/tickets/{ticket_id}")

        assert response.status_code == 403, response.get_data(as_text=True)

        data = response.get_json()

        assert data["error"] == "Forbidden"

def test_resolver_can_view_assigned_ticket_detail(tmp_path):
    app = create_app()
    database_path = tmp_path / "tickets.db"
    app.config["DATABASE"] = str(database_path)
    app.config["TESTING"] = True

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
                "Assigned ticket detail",
                "Resolver should be able to view this assigned ticket.",
                "open",
                "account_access",
                requester["id"],
                resolver["id"],
            )
        )

        ticket_id = ticket_cursor.lastrowid

        db.commit()
    
    client = app.test_client()

    login_response = client.post(
        "/api/auth/login",
        json={
            "username": "resolver_demo",
            "password": "resolver123",
        }
    )

    assert login_response.status_code == 200, login_response.get_data(as_text=True)

    response = client.get(f"/api/tickets/{ticket_id}")

    assert response.status_code == 200, response.get_data(as_text=True)

    data = response.get_json()

    assert "ticket" in data
    
    ticket = data["ticket"]

    assert ticket["id"] == ticket_id
    assert ticket["title"] == "Assigned ticket detail"
    assert ticket["description"] == "Resolver should be able to view this assigned ticket."
    assert ticket["status"] == "open"
    assert ticket["category"] == "account_access"

def test_resolver_cannot_view_ticket_assigned_to_another_resolver(tmp_path):
    app = create_app()
    database_path = tmp_path / "tickets.db"
    app.config["DATABASE"] = str(database_path)
    app.config["TESTING"] = True

    with app.app_context():
        init_db()
        seed_db()

        db = get_db()

        requester = db.execute(
            "SELECT id FROM users WHERE username = ?",
            ("requester_demo",)
        ).fetchone()

        other_resolver_cursor = db.execute(
            """
            INSERT INTO users (username, password_hash, role, is_seeded)
            VALUES (?, ?, ?, ?)
            """,
            ("other_resolver", "not-used", "resolver", 0)
        )

        other_resolver_id = other_resolver_cursor.lastrowid

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
                "Other resolver detail",
                "resolver_demo should not be able to view this ticket.",
                "open",
                "account_access",
                requester["id"],
                other_resolver_id,
            )
        )

        ticket_id = ticket_cursor.lastrowid

        db.commit()

    client = app.test_client()

    login_response = client.post(
        "/api/auth/login",
        json={
            "username": "resolver_demo",
            "password": "resolver123",
        }
    )

    assert login_response.status_code == 200, login_response.get_data(as_text=True)

    response = client.get(f"/api/tickets/{ticket_id}")

    assert response.status_code == 403, response.get_data(as_text=True)

    data = response.get_json()

    assert data["error"] == "Forbidden"

def test_logged_in_user_gets_404_for_missing_ticket_detail(tmp_path):
    app = create_app()
    database_path = tmp_path / "tickets.db"
    app.config["DATABASE"] = str(database_path)
    app.config["TESTING"] = True

    with app.app_context():
        init_db()
        seed_db()

    client = app.test_client()

    login_response = client.post(
        "/api/auth/login",
        json={
            "username": "requester_demo",
            "password": "requester123",
        },
    )

    assert login_response.status_code == 200, login_response.get_data(as_text=True)

    response = client.get("api/tickets/999")

    assert response.status_code == 404, response.get_data(as_text=True)

    data = response.get_json()

    assert data["error"] == "Ticket not found"

def test_unauthenticated_user_cannot_add_ticket_note(tmp_path):
    app = create_app()
    database_path = tmp_path / "tickets.db"
    app.config["DATABASE"] = str(database_path)
    app.config["TESTING"] = True

    with app.app_context():
        init_db()
        seed_db()

    client = app.test_client()

    response = client.post(
        "/api/tickets/1/notes",
        json={
            "body": "This note should not be created.",
        },
    )

    assert response.status_code == 401, response.get_data(as_text=True)

    data = response.get_json()

    assert data["error"] == "Not authenticated"

def test_requester_can_add_note_to_own_ticket(tmp_path):
    app = create_app()
    database_path = tmp_path / "tickets.db"
    app.config["DATABASE"] = str(database_path)
    app.config["TESTING"] = True

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
                "Ticket needing requester note",
                "Requester should be able to add a note",
                "open",
                "account_access",
                requester["id"],
                resolver["id"]
            )
        )

        ticket_id = ticket_cursor.lastrowid

        db.commit()

    client = app.test_client()

    login_response = client.post(
        "api/auth/login",
        json={
            "username": "requester_demo",
            "password": "requester123",
        },
    )

    assert login_response.status_code == 200, login_response.get_data(as_text=True)

    response = client.post(
        f"/api/tickets/{ticket_id}/notes",
        json={
            "body": "I am still having trouble accessing my account."
        },
    )

    assert response.status_code == 201, response.get_data(as_text=True)

    data = response.get_json()

    assert "note" in data
    assert data["note"]["body"] == "I am still having trouble accessing my account."
    assert data["note"]["note_type"] == "requester_note"

    with app.app_context():
        db = get_db()

        note = db.execute(
            """
            SELECT ticket_id, author_id, note_type, body
            FROM ticket_notes
            WHERE ticket_id = ?
            """,
            (ticket_id,)
        ).fetchone()

        assert note is not None
        assert note["ticket_id"] == ticket_id
        assert note["author_id"] == requester["id"]
        assert note["note_type"] == "requester_note"
        assert note["body"] == "I am still having trouble accessing my account."

def test_resolver_can_add_note_to_assigned_ticket(tmp_path):
    app = create_app()
    database_path = tmp_path / "tickets.db"
    app.config["DATABASE"] = str(database_path)
    app.config["TESTING"] = True
    
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
                "Ticket needing resolver note",
                "Resolver should be able to add note.",
                "open",
                "account_access",
                requester["id"],
                resolver["id"],
            )
        )

        ticket_id = ticket_cursor.lastrowid
        
        db.commit()

    client = app.test_client()

    login_response = client.post(
        "/api/auth/login",
        json={
            "username": "resolver_demo",
            "password": "resolver123",
        },
    )

    assert login_response.status_code == 200, login_response.get_data(as_text=True)

    response = client.post(
        f"/api/tickets/{ticket_id}/notes",
        json={
            "body": "I am reviewing this account access issue.",
        },
    )

    assert response.status_code == 201, response.get_data(as_text=True)

    data = response.get_json()

    assert "note" in data
    assert data["note"]["body"] == "I am reviewing this account access issue."
    assert data["note"]["note_type"] == "resolver_note"

    with app.app_context():
        db = get_db()

        note = db.execute(
            """
            SELECT ticket_id, author_id, note_type, body
            FROM ticket_notes
            WHERE ticket_id = ?
            """,
            (ticket_id,)
        ).fetchone()

        assert note is not None
        assert note["ticket_id"] == ticket_id
        assert note["author_id"] == resolver["id"]
        assert note["note_type"] == "resolver_note"
        assert note["body"] == "I am reviewing this account access issue."

def test_requester_cannot_add_note_to_another_requesters_ticket(tmp_path):
    app = create_app()
    database_path = tmp_path / "tickets.db"
    app.config["DATABASE"] = str(database_path)
    app.config["TESTING"] = True

    with app.app_context():
        init_db()
        seed_db()

        db = get_db()

        resolver = db.execute(
            "SELECT id FROM users WHERE username = ?",
            ("resolver_demo",)
        ).fetchone()

        other_requester_cursor = db.execute(
            """
            INSERT INTO users (username, password_hash, role, is_seeded)
            VALUES (?, ?, ?, ?)
            """,
            ("other_requester", "not-used", "requester", 0)
        )

        other_requester_id = other_requester_cursor.lastrowid

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
                "Other requester note test",
                "requester_demo should not add notes to this ticket.",
                "open",
                "account_access",
                other_requester_id,
                resolver["id"],
            )
        )

        ticket_id = ticket_cursor.lastrowid
        
        db.commit()

    client = app.test_client()

    login_response = client.post(
        "/api/auth/login",
        json={
            "username": "requester_demo",
            "password": "requester123",
        },
    )

    assert login_response.status_code == 200, login_response.get_data(as_text=True)

    response = client.post(
        f"/api/tickets/{ticket_id}/notes",
        json={
            "body": "Trying to add a note to someone else's ticket.",
        },
    )

    assert response.status_code == 403, response.get_data(as_test=True)

    data = response.get_json()

    assert data["error"] == "Forbidden"

    with app.app_context():
        db = get_db()

        notes = db.execute(
            """
            SELECT id
            FROM ticket_notes
            WHERE ticket_id = ?
            """,
            (ticket_id,)
        ).fetchall()

        assert len(notes) == 0

def test_resolver_cannot_add_note_to_ticket_assigned_to_another_resolver(tmp_path):
    app = create_app()
    database_path = tmp_path / "tickets.db"
    app.config["DATABASE"] = str(database_path)
    app.config["TESTING"] = True

    with app.app_context():
        init_db()
        seed_db()

        db = get_db()

        requester = db.execute(
            "SELECT id FROM users WHERE username = ?",
            ("requester_demo",)
        ).fetchone()

        other_resolver_cursor = db.execute(
            """
            INSERT INTO users (username, password_hash, role, is_seeded)
            VALUES (?, ?, ?, ?)
            """,
            ("other_resolver", "not-used", "resolver", 0)
        )

        other_resolver_id = other_resolver_cursor.lastrowid
        
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
                "Other resolver note test",
                "resolver_demo should not add notes to this ticket.",
                "open",
                "account_access",
                requester["id"],
                other_resolver_id,
            )
        )

        ticket_id = ticket_cursor.lastrowid
        
        db.commit()

    client = app.test_client()

    login_response = client.post(
        "/api/auth/login",
        json={
            "username": "resolver_demo",
            "password": "resolver123",
        },
    )

    assert login_response.status_code == 200, login_response.get_data(as_text=True)

    response = client.post(
        f"/api/tickets/{ticket_id}/notes",
        json={
            "body": "Trying to add a note to another resolver's ticket.",
        },
    )

    assert response.status_code == 403, response.get_data(as_text=True)

    data = response.get_json()

    assert data["error"] == "Forbidden"

    with app.app_context():
        db = get_db()

        notes = db.execute(
            """
            SELECT id
            FROM ticket_notes
            WHERE ticket_id = ?
            """,
            (ticket_id,)
        ).fetchall()

        assert len(notes) == 0

def test_logged_in_user_gets_404_when_adding_note_to_missing_ticket(tmp_path):
    app = create_app()
    database_path = tmp_path / "tickets.db"
    app.config["DATABASE"] = str(database_path)
    app.config["TESTING"] = True

    with app.app_context():
        init_db()
        seed_db()

    client = app.test_client()

    login_response = client.post(
        "/api/auth/login",
        json={
            "username": "requester_demo",
            "password": "requester123",
        },
    )

    assert login_response.status_code == 200, login_response.get_data(as_text=True)

    response = client.post(
        "/api/tickets/999/notes",
        json={
            "body": "This ticket should not exist.",
        },
    )

    assert response.status_code == 404, response.get_data(as_text=True)

    data = response.get_json()

    assert data["error"] == "Ticket not found"

    with app.app_context():
        db = get_db()

        notes = db.execute(
            "SELECT id FROM ticket_notes"
        ).fetchall()

        assert len(notes) == 0

def test_cannot_add_note_without_body(tmp_path):
    app = create_app()
    database_path = tmp_path / "tickets.db"
    app.config["DATABASE"] = str(database_path)
    app.config["TESTING"] = True

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
                "Missing note body test",
                "Requester should not be able to add an empty note.",
                "open",
                "account_access",
                requester["id"],
                resolver["id"],
            )
        )

        ticket_id = ticket_cursor.lastrowid

        db.commit()

    client = app.test_client()

    login_response = client.post(
        "/api/auth/login",
        json={
            "username": "requester_demo",
            "password": "requester123",
        },
    )

    assert login_response.status_code == 200, login_response.get_data(as_text=True)

    response = client.post(
        f"/api/tickets/{ticket_id}/notes",
        json={}
    )

    assert response.status_code == 400, response.get_data(as_text=True)

    data = response.get_json()

    assert data["error"] == "Note body is required"

    with app.app_context():
        db = get_db()

        notes = db.execute(
            "SELECT id FROM ticket_notes WHERE ticket_id = ?",
            (ticket_id,)
        ).fetchall()

        assert len(notes) == 0

def test_cannot_add_note_with_empty_body(tmp_path):
    app = create_app()
    database_path = tmp_path / "tickets.db"
    app.config["DATABASE"] = str(database_path)
    app.config["TESTING"] = True

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
                "Empty note body test",
                "Requester should not be able to add an empty note.",
                "open",
                "account_access",
                requester["id"],
                resolver["id"],
            )
        )

        ticket_id = ticket_cursor.lastrowid

        db.commit()

    client = app.test_client()

    login_response = client.post(
        "/api/auth/login",
        json={
            "username": "requester_demo",
            "password": "requester123",
        },
    )

    assert login_response.status_code == 200, login_response.get_data(as_text=True)

    response = client.post(
        f"/api/tickets/{ticket_id}/notes",
        json={
            "body": "",
        },
    )

    assert response.status_code == 400, response.get_data(as_text=True)

    data = response.get_json()

    assert data["error"] == "Note body is required"

    with app.app_context():
        db = get_db()

        notes = db.execute(
            "SELECT id FROM ticket_notes WHERE ticket_id = ?",
            (ticket_id,)
        ).fetchall()

        assert len(notes) == 0

def test_cannot_add_note_with_whitespace_only_body(tmp_path):
    app = create_app()
    database_path = tmp_path / "tickets.db"
    app.config["DATABASE"] = str(database_path)
    app.config["TESTING"] = True

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
                "Whitespace note body test",
                "Requester should not be able to add a whitespace only note.",
                "open",
                "account_access",
                requester["id"],
                resolver["id"],
            )
        )

        ticket_id = ticket_cursor.lastrowid

        db.commit()

    client = app.test_client()

    login_response = client.post(
        "/api/auth/login",
        json={
            "username": "requester_demo",
            "password": "requester123",
        },
    )

    assert login_response.status_code == 200, login_response.get_data(as_text=True)

    response = client.post(
        f"/api/tickets/{ticket_id}/notes",
        json={
            "body": "   ",
        },
    )

    assert response.status_code == 400, response.get_data(as_text=True)

    data = response.get_json()

    assert data["error"] == "Note body is required"

    with app.app_context():
        db = get_db()

        notes = db.execute(
            "SELECT id FROM ticket_notes WHERE ticket_id = ?",
            (ticket_id,)
        ).fetchall()

        assert len(notes) == 0

def test_note_body_is_trimmed_before_saving(tmp_path):
    app = create_app()
    database_path = tmp_path / "tickets.db"
    app.config["DATABASE"] = str(database_path)
    app.config["TESTING"] = True

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
                "Trim note body test",
                "Valid note should be trimmed before saving.",
                "open",
                "account_access",
                requester["id"],
                resolver["id"],
            )
        )

        ticket_id = ticket_cursor.lastrowid

        db.commit()

    client = app.test_client()

    login_response = client.post(
        "/api/auth/login",
        json={
            "username": "requester_demo",
            "password": "requester123",
        },
    )

    assert login_response.status_code == 200, login_response.get_data(as_text=True)

    response = client.post(
        f"/api/tickets/{ticket_id}/notes",
        json={
            "body": "    I still cannot access my account.      ",
        },
    )

    assert response.status_code == 201, response.get_data(as_text=True)

    data = response.get_json()

    assert data["note"]["body"] == "I still cannot access my account."

    with app.app_context():
        db = get_db()

        note = db.execute(
            """
            SELECT body
            FROM ticket_notes
            WHERE ticket_id = ?
            """,
            (ticket_id,)
        ).fetchone()

        assert note is not None
        assert note["body"] == "I still cannot access my account."

def test_ticket_detail_includes_notes_for_authorized_user(tmp_path):
    app = create_app()
    database_path = tmp_path / "tickets.db"
    app.config["DATABASE"] = str(database_path)
    app.config["TESTING"] = True

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
                "Ticket with notes",
                "This ticket should return its notes in the detail response.",
                "open",
                "account_access",
                requester["id"],
                resolver["id"],
            )
        )

        ticket_id = ticket_cursor.lastrowid

        db.execute(
            """
            INSERT INTO ticket_notes (
            ticket_id,
            author_id,
            note_type,
            body
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                ticket_id,
                requester["id"],
                "requester_note",
                "This is note one of two.",
            )
        )

        db.execute(
            """
            INSERT INTO ticket_notes (
            ticket_id,
            author_id,
            note_type,
            body
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                ticket_id,
                resolver["id"],
                "resolver_note",
                "This is note two of two.",
            )
        )

        db.commit()

    client = app.test_client()

    login_response = client.post(
        "/api/auth/login",
        json={
            "username": "requester_demo",
            "password": "requester123",
        },
    )

    assert login_response.status_code == 200, login_response.get_data(as_text=True)

    response = client.get(f"/api/tickets/{ticket_id}")

    assert response.status_code == 200, response.get_data(as_text=True)

    data = response.get_json()

    assert "ticket" in data
    assert "notes" in data["ticket"]

    notes = data["ticket"]["notes"]

    assert len(notes) == 2

    assert notes[0]["body"] == "This is note one of two."
    assert notes[0]["note_type"] == "requester_note"

    assert notes[1]["body"] == "This is note two of two."
    assert notes[1]["note_type"] == "resolver_note"

def test_ticket_detail_returns_empty_notes_list_when_no_notes_exist(tmp_path):
    app = create_app()
    database_path = tmp_path / "tickets.db"
    app.config["DATABASE"] = str(database_path)
    app.config["TESTING"] = True

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
                "Ticket with no notes",
                "This ticket should return an empty notes list.",
                "open",
                "account_access",
                requester["id"],
                resolver["id"],
            )
        )

        ticket_id = ticket_cursor.lastrowid
        
        db.commit()

    client = app.test_client()

    login_response = client.post(
        "/api/auth/login",
        json={
            "username": "requester_demo",
            "password": "requester123",
        },
    )

    assert login_response.status_code == 200, login_response.get_data(as_text=True)

    response = client.get(f"/api/tickets/{ticket_id}")

    assert response.status_code == 200, response.get_data(as_text=True)

    data = response.get_json()

    assert "ticket" in data
    assert "notes" in data["ticket"]
    assert data["ticket"]["notes"] == []

def test_unauthenticated_user_cannot_update_ticket_status(tmp_path):
    app = create_app()
    database_path = tmp_path / "tickets.db"
    app.config["DATABASE"] = str(database_path)
    app.config["TESTING"] = True
    
    with app.app_context():
        init_db()
        seed_db()

    client = app.test_client()

    response = client.patch(
        "api/tickets/1/status",
        json={
            "status": "in_progress",
        },
    )

    assert response.status_code == 401, response.get_data(as_text=True)

    data = response.get_json()

    assert data["error"] == "Not authenticated"

def test_requester_cannot_update_ticket_status(tmp_path):
    app = create_app()
    database_path = tmp_path / "tickets.db"
    app.config["DATABASE"] = str(database_path)
    app.config["TESTING"] = True

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
                "Requester status update test",
                "Requester should not be able to update status.",
                "open",
                "account_access",
                requester["id"],
                resolver["id"],
            )
        )

        ticket_id = ticket_cursor.lastrowid

        db.commit()

    client = app.test_client()

    login_response = client.post(
        "/api/auth/login",
        json={
            "username": "requester_demo",
            "password": "requester123",
        },
    )

    assert login_response.status_code == 200, login_response.get_data(as_text=True)

    response = client.patch(
        f"api/tickets/{ticket_id}/status",
        json={
            "status": "in_progress",
        },
    )

    assert response.status_code == 403, response.get_data(as_text=True)

    data = response.get_json()

    assert data["error"] == "Forbidden"

    with app.app_context():
        db = get_db()

        ticket = db.execute(
            """
            SELECT status
            FROM tickets
            WHERE id = ?
            """,
            (ticket_id,)
        ).fetchone()

        assert ticket["status"] == "open"

def test_resolver_gets_404_when_updating_missing_ticket_status(tmp_path):
    app = create_app()
    database_path = tmp_path / "tickets.db"
    app.config["DATABASE"] = str(database_path)
    app.config["TESTING"] = True

    with app.app_context():
        init_db()
        seed_db()

    client = app.test_client()

    login_response = client.post(
        "/api/auth/login",
        json={
            "username": "resolver_demo",
            "password": "resolver123",
        },
    )

    assert login_response.status_code == 200, login_response.get_data(as_text=True)

    response = client.patch(
        "/api/tickets/999/status",
        json={
            "status": "in_progress",
        },
    )

    assert response.status_code == 404, response.get_data(as_text=True)

    data = response.get_json()

    assert data["error"] == "Ticket not found"

def test_resolver_cannot_update_status_for_ticket_assigned_to_another_resolver(tmp_path):
    app = create_app()
    database_path = tmp_path / "tickets.db"
    app.config["DATABASE"] = str(database_path)
    app.config["TESTING"] = True

    with app.app_context():
        init_db()
        seed_db()

        db = get_db()

        requester = db.execute(
            "SELECT id FROM users WHERE username = ?",
            ("requester_demo",)
        ).fetchone()

        other_resolver_cursor = db.execute(
            """
            INSERT INTO users (username, password_hash, role, is_seeded)
            VALUES (?, ?, ?, ?)
            """,
            (
                "other_resolver",
                "temporary_hash_for_test",
                "resolver",
                0,
            )
        )

        other_resolver_id = other_resolver_cursor.lastrowid

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
                "Assigned to other resolver",
                "resolver_demo should not be able to update this ticket.",
                "open",
                "account_access",
                requester["id"],
                other_resolver_id,
            )
        )

        ticket_id = ticket_cursor.lastrowid

        db.commit()

    client = app.test_client()

    login_response = client.post(
        "/api/auth/login",
        json={
            "username": "resolver_demo",
            "password": "resolver123",
        },
    )

    assert login_response.status_code == 200, login_response.get_data(as_text=True)

    response = client.patch(
        f"/api/tickets/{ticket_id}/status",
        json={
            "status": "in_progress",
        },
    )

    assert response.status_code == 403, response.get_data(as_text=True)

    data = response.get_json()

    assert data["error"] == "Forbidden"

    with app.app_context():
        db = get_db()

        ticket = db.execute(
            """
            SELECT status
            FROM tickets
            WHERE id = ?
            """,
            (ticket_id,)
        ).fetchone()

        assert ticket["status"] == "open"

def test_assigned_resolver_can_update_ticket_status(tmp_path):
    app = create_app()
    database_path = tmp_path / "tickets.db"
    app.config["DATABASE"] = str(database_path)
    app.config["TESTING"] = True

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
                "Assigned resolver status update",
                "resolver_demo should be able to update this ticket.",
                "open",
                "account_access",
                requester["id"],
                resolver["id"],
            )
        )

        ticket_id = ticket_cursor.lastrowid

        db.commit()

    client = app.test_client()

    login_response = client.post(
        "/api/auth/login",
        json={
            "username": "resolver_demo",
            "password": "resolver123",
        },
    )

    assert login_response.status_code == 200, login_response.get_data(as_text=True)

    response = client.patch(
        f"/api/tickets/{ticket_id}/status",
        json={
            "status": "in_progress",
        },
    )

    assert response.status_code == 200, response.get_data(as_text=True)

    data = response.get_json()

    assert data["ticket"]["id"] == ticket_id
    assert data["ticket"]["status"] == "in_progress"

    with app.app_context():
        db = get_db()

        ticket = db.execute(
            """
            SELECT status
            FROM tickets
            WHERE id = ?
            """,
            (ticket_id,)
        ).fetchone()

        assert ticket["status"] == "in_progress"

def test_assigned_resolver_cannot_update_ticket_status_to_invalid_value(tmp_path):
    app = create_app()
    database_path = tmp_path / "tickets.db"
    app.config["DATABASE"] = str(database_path)
    app.config["TESTING"] = True

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
                "Invalid status update.",
                "resolver_demo should not be able to set an invalid status.",
                "open",
                "account_access",
                requester["id"],
                resolver["id"],
            )
            
        )

        ticket_id = ticket_cursor.lastrowid

        db.commit()

    client = app.test_client()

    login_response = client.post(
        "/api/auth/login",
        json={
            "username": "resolver_demo",
            "password": "resolver123",
        },
    )

    assert login_response.status_code == 200, login_response.get_data(as_text=True)

    response = client.patch(
        f"/api/tickets/{ticket_id}/status",
        json={
            "status": "closed",
        },
    )

    assert response.status_code == 400, response.get_data(as_text=True)

    data = response.get_json()

    assert data["error"] == "Invalid status"

    with app.app_context():
        db = get_db()

        ticket = db.execute(
            """
            SELECT status
            FROM tickets
            WHERE id = ?
            """,
            (ticket_id,)
        ).fetchone()

        assert ticket["status"] == "open"

def test_assigned_resolver_cannot_update_ticket_status_without_status_field(tmp_path):
    app = create_app()
    database_path = tmp_path / "tickets.db"
    app.config["DATABASE"] = str(database_path)
    app.config["TESTING"] = True

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
                "Missing status field",
                "The request should fail if status is missing.",
                "open",
                "account_access",
                requester["id"],
                resolver["id"],
            )
        )

        ticket_id = ticket_cursor.lastrowid

        db.commit()

    client = app.test_client()

    login_response = client.post(
        "/api/auth/login",
        json={
            "username": "resolver_demo",
            "password": "resolver123",
        },
    )

    assert login_response.status_code == 200, login_response.get_data(as_text=True)

    response = client.patch(
        f"/api/tickets/{ticket_id}/status",
        json={},
    )

    assert response.status_code == 400, response.get_data(as_text=True)

    data = response.get_json()

    assert data["error"] == "Invalid status"

    with app.app_context():
        db = get_db()

        ticket = db.execute(
            """
            SELECT status
            FROM tickets
            WHERE id = ?
            """,
            (ticket_id,)
        ).fetchone()

        assert ticket["status"] == "open"

def test_status_update_creates_status_update_note(tmp_path):
    app = create_app()
    database_path = tmp_path / "tickets.db"
    app.config["DATABASE"] = str(database_path)
    app.config["TESTING"] = True

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
                "Status update note test",
                "Changing status should create a status_update note.",
                "open",
                "account_access",
                requester["id"],
                resolver["id"],
            )
        )

        ticket_id = ticket_cursor.lastrowid

        db.commit()

    client = app.test_client()

    login_response = client.post(
        "/api/auth/login",
        json={
            "username": "resolver_demo",
            "password": "resolver123",
        },
    )

    assert login_response.status_code == 200, login_response.get_data(as_text=True)

    response = client.patch(
        f"/api/tickets/{ticket_id}/status",
        json={
            "status": "in_progress",
        },
    )
    
    assert response.status_code == 200, response.get_data(as_text=True)

    with app.app_context():
        db = get_db()

        note = db.execute(
            """
            SELECT ticket_id, author_id, note_type, body
            FROM ticket_notes
            WHERE ticket_id = ?
            """,
            (ticket_id,)
        ).fetchone()

        assert note is not None
        assert note["ticket_id"] == ticket_id
        assert note["author_id"] == resolver["id"]
        assert note["note_type"] == "status_update"
        assert note["body"] == "Status changed from open to in_progress."

def test_ticket_detail_includes_status_update_note_after_status_change(tmp_path):
    app = create_app()
    database_path = tmp_path / "tickets.db"
    app.config["DATABASE"] = str(database_path)
    app.config["TESTING"] = True

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
                "Status history detail test",
                "Ticket detail should include the status update note.",
                "open",
                "account_access",
                requester["id"],
                resolver["id"],
            )
        )

        ticket_id = ticket_cursor.lastrowid

        db.commit()

    client = app.test_client()

    resolver_login_response = client.post(
        "/api/auth/login",
        json={
            "username": "resolver_demo",
            "password": "resolver123",
        },
    )

    assert resolver_login_response.status_code == 200, resolver_login_response.get_data(as_text=True)

    status_response = client.patch(
        f"/api/tickets/{ticket_id}/status",
        json={
            "status": "in_progress",
        },
    )

    assert status_response.status_code == 200, status_response.get_data(as_text=True)

    client.post("/api/auth/logout")

    requester_login_response = client.post(
        "/api/auth/login",
        json={
            "username": "requester_demo",
            "password": "requester123",
        },
    )

    assert requester_login_response.status_code == 200, requester_login_response.get_data(as_text=True)

    detail_response = client.get(f"/api/tickets/{ticket_id}")

    assert detail_response.status_code == 200, detail_response.get_data(as_text=True)

    data = detail_response.get_json()

    notes = data["ticket"]["notes"]

    assert len(notes) == 1
    assert notes[0]["note_type"] == "status_update"
    assert notes[0]["body"] == "Status changed from open to in_progress."
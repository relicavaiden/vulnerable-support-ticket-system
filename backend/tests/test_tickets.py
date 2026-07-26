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
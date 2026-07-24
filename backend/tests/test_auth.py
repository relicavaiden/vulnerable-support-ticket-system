from app import create_app
from app.db import init_db
from app.seed import seed_db


def test_login_with_valid_seed_user_returns_user(tmp_path):
    app = create_app()
    database_path = tmp_path / "auth.db"
    app.config["DATABASE"] = str(database_path)

    with app.app_context():
        init_db()
        seed_db()

    client = app.test_client()

    response = client.post(
        "/api/auth/login",
        json={
            "username": "requester_demo",
            "password": "requester123",
        },
    )

    assert response.status_code == 200

    data = response.get_json()

    assert "user" in data
    assert data["user"]["username"] == "requester_demo"
    assert data["user"]["role"] == "requester"
    assert "password_hash" not in data["user"]
    assert "password" not in data["user"]

    with client.session_transaction() as session_data:
        assert session_data["user_id"] == data["user"]["id"]

def test_login_with_wrong_password_returns_401(tmp_path):
    app = create_app()
    database_path = tmp_path / "auth.db"
    app.config["DATABASE"] = str(database_path)

    with app.app_context():
        init_db()
        seed_db()

    client = app.test_client()

    response = client.post(
        "/api/auth/login",
        json={
            "username": "requester_demo",
            "password": "wrong-password",
        },
    )

    assert response.status_code == 401

    data = response.get_json()

    assert data["error"] == "Invalid username or password"


def test_login_with_unknown_usernam_returns_401(tmp_path):
    app = create_app()
    database_path = tmp_path / "auth.db"
    app.config["DATABASE"] = str(database_path)

    with app.app_context():
        init_db()
        seed_db()

    client = app.test_client()

    response = client.post(
        "/api/auth/login",
        json={
            "username": "not_a_real_user",
            "password": "requester123",
        },
    )

    assert response.status_code == 401

    data = response.get_json()

    assert data["error"] == "Invalid username or password"

def test_me_without_login_returns_401(tmp_path):
    app = create_app()
    database_path = tmp_path / "auth.db"
    app.config["DATABASE"] = str(database_path)

    with app.app_context():
        init_db()
        seed_db()

    client = app.test_client()

    response = client.get("/api/auth/me")

    assert response.status_code == 401

def test_me_after_login_returns_current_user(tmp_path):
    app = create_app()
    database_path = tmp_path / "auth.db"
    app.config["DATABASE"] = str(database_path)

    with app.app_context():
        init_db()
        seed_db()

    client = app.test_client()

    client.post(
        "/api/auth/login",
        json={
            "username": "requester_demo",
            "password": "requester123",
        },
    )

    response = client.get("/api/auth/me")

    assert response.status_code == 200

    data = response.get_json()

    assert data["user"]["username"] == "requester_demo"
    assert data["user"]["role"] == "requester"
    assert "password_hash" not in data["user"]
    assert "password" not in data["user"]

def test_me_with_invalid_session_user_returns_401(tmp_path):
    app = create_app()
    database_path = tmp_path / "auth.db"
    app.config["DATABASE"] = str(database_path)

    with app.app_context():
        init_db()
        seed_db()

    client = app.test_client()

    with client.session_transaction() as session_data:
        session_data["user_id"] = 999

    response = client.get("/api/auth/me")

    assert response.status_code == 401

    data = response.get_json()

    assert data["error"] == "Not authenticated"

def test_logout_clears_session(tmp_path):
    app = create_app()
    database_path = tmp_path / "auth.db"
    app.config["DATABASE"] = str(database_path)

    with app.app_context():
        init_db()
        seed_db()

    client = app.test_client()

    client.post(
        "/api/auth/login",
        json={
            "username": "requester_demo",
            "password": "requester123",
        },
    )

    with client.session_transaction() as session_data:
        assert "user_id" in session_data

    response = client.post("/api/auth/logout")

    assert response.status_code == 200

    with client.session_transaction() as session_data:
        assert "user_id" not in session_data

    data = response.get_json()

    assert data["message"] == "Logged out successfully"

def test_me_after_logout_returns_401(tmp_path):
    app = create_app()
    database_path = tmp_path / "auth.db"
    app.config["DATABASE"] = str(database_path)

    with app.app_context():
        init_db()
        seed_db()

    client = app.test_client()

    client.post(
        "/api/auth/login",
        json={
            "username": "requester_demo",
            "password": "requester123",
        },
    )

    logout_response = client.post("/api/auth/logout")

    assert logout_response.status_code == 200

    response = client.get("/api/auth/me")

    assert response.status_code == 401

    data = response.get_json()

    assert data["error"] == "Not authenticated"
from app import create_app
from app.db import get_db, init_db
from app.seed import seed_db

def test_creates_seed_users_without_duplicates(app):
    with app.app_context():
        init_db()
        seed_db()

        users = get_db().execute(
            "SELECT username, role, is_seeded FROM users ORDER BY username"
        ).fetchall()

        assert len(users) == 2

        assert users[0]["username"] == "requester_demo"
        assert users[0]["role"] == "requester"
        assert users[0]["is_seeded"] == 1

        assert users[1]["username"] == "resolver_demo"
        assert users[1]["role"] == "resolver"
        assert users[1]["is_seeded"] == 1

        seed_db()

        users_after_second_seed = get_db().execute(
            "SELECT username, role, is_seeded FROM users ORDER BY username"
        ).fetchall()

        assert len(users_after_second_seed) == 2
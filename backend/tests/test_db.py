from app import create_app
from app.db import get_db, init_db


def test_init_db_creates_expected_tables(app):
    with app.app_context():
        init_db()
        db = get_db()
        tables = db.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
        ).fetchall()
        table_names = { table["name"] for table in tables }

    assert table_names == { "users", "tickets", "ticket_notes", "login_rate_limits" }
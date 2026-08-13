import click

from werkzeug.security import generate_password_hash

from app.db import get_db

def seed_db():
    db = get_db()

    seed_users = [
        {
            "username": "requester_demo",
            "password": "requester123",
            "role": "requester",
        },
        {
            "username": "resolver_demo",
            "password": "resolver123",
            "role": "resolver",
        },
    ]

    for user in seed_users:
        existing_user = db.execute(
            "SELECT id FROM users WHERE username = ?", (user["username"],)
        ).fetchone()

        if existing_user is None:
            db.execute(
                """
                INSERT INTO users (username, password_hash, role, is_seeded) 
                VALUES (?, ?, ?, ?)
                """,
                (
                
                    user["username"], 
                    generate_password_hash(user["password"]), 
                    user["role"], 
                    1,
                ),
            )

    db.commit()

@click.command("seed-db")
def seed_db_command():
    seed_db()
    click.echo("Database seeded successfully.")

def init_app(app):
    app.cli.add_command(seed_db_command)
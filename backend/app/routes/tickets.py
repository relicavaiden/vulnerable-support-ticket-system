from flask import Blueprint, jsonify, request, session

from app.db import get_db

tickets_bp = Blueprint("tickets", __name__, url_prefix="/api")

@tickets_bp.get("/tickets")
def get_tickets():
    user_id = session.get("user_id")

    if user_id is None:
        return jsonify({"error": "Not authenticated"}), 401
    
    db = get_db()

    user = db.execute(
        "SELECT id, username, role FROM users WHERE id = ?",
        (user_id,)
    ).fetchone()

    if user is None:
        return jsonify({"error": "Not authenticated"}), 401
    
    if user["role"] == "requester":
        tickets = db.execute(
            """
            SELECT id, title, description, status, category
            FROM tickets
            WHERE requester_id = ?
            ORDER BY created_at DESC
            """,
            (user["id"],)
        ).fetchall()
    elif user["role"] == "resolver":
        tickets = db.execute(
            """
            SELECT id, title, description, status, category
            FROM tickets
            WHERE assigned_resolver_id = ?
            ORDER BY created_at DESC
            """,
            (user["id"],)
        ).fetchall()
    else:
        return jsonify({"error": "Forbidden"}), 403

    return jsonify({
        "tickets": [
            {
                "id": ticket["id"],
                "title": ticket["title"],
                "description": ticket["description"],
                "status": ticket["status"],
                "category": ticket["category"],
            }
            for ticket in tickets
        ]
    }), 200

@tickets_bp.post("/tickets")
def create_ticket():
    user_id = session.get("user_id")

    if user_id is None:
        return jsonify({"error": "Not authenticated"}), 401
    
    db = get_db()

    user = db.execute(
        "SELECT id, username, role FROM users WHERE id = ?",
        (user_id,)
    ).fetchone()

    if user is None:
        return jsonify({"error": "Not authenticated"}), 401
    
    if user["role"] != "requester":
        return jsonify({"error": "Forbidden"}), 403
    
    data = request.get_json() or {}

    title = data.get("title")
    description = data.get("description")
    category = data.get("category")

    resolver = db.execute(
        "SELECT id FROM users WHERE role = ? ORDER BY id LIMIT 1",
        ("resolver",)
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
            title,
            description,
            "open",
            category,
            user["id"],
            resolver["id"],
        ),
    )

    db.commit()

    ticket = db.execute(
        """
        SELECT id, title, description, status, category, requester_id, assigned_resolver_id
        FROM tickets
        WHERE title = ?
        """,
        (title,)
    ).fetchone()

    return jsonify({
        "ticket": {
            "id": ticket["id"],
            "title": ticket["title"],
            "description": ticket["description"],
            "status": ticket["status"],
            "category": ticket["category"],
            }
    }), 201
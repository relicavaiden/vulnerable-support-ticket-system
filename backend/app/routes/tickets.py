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
            title,
            description,
            "open",
            category,
            user["id"],
            resolver["id"],
        ),
    )

    db.commit()

    ticket_id = ticket_cursor.lastrowid

    ticket = db.execute(
        """
        SELECT id, title, description, status, category, requester_id, assigned_resolver_id
        FROM tickets
        WHERE id = ?
        """,
        (ticket_id,)
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

@tickets_bp.get("/tickets/<int:ticket_id>")
def get_ticket_detail(ticket_id):
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
    
    ticket = db.execute(
        """
        SELECT id, title, description, status, category, requester_id, assigned_resolver_id
        FROM tickets
        WHERE id = ?
        """,
        (ticket_id,)
    ).fetchone()

    if ticket is None:
        return jsonify({"error": "Ticket not found"}), 404
    
    if user["role"] == "requester" and ticket["requester_id"] != user["id"]:
        return jsonify({"error": "Forbidden"}), 403
    
    if user["role"] == "resolver" and ticket["assigned_resolver_id"] != user["id"]:
        return jsonify({"error": "Forbidden"}), 403
    
    notes = db.execute(
        """
        SELECT 
            ticket_notes.id,
            ticket_notes.ticket_id,
            ticket_notes.author_id,
            users.username AS author_username,
            ticket_notes.note_type,
            ticket_notes.body,
            ticket_notes.created_at
        FROM ticket_notes
        JOIN users ON users.id = ticket_notes.author_id
        WHERE ticket_notes.ticket_id = ?
        ORDER BY ticket_notes.id ASC
        """,
        (ticket_id,)
    ).fetchall()
    
    return jsonify({
        "ticket": {
            "id": ticket["id"],
            "title": ticket["title"],
            "description": ticket["description"],
            "status": ticket["status"],
            "category": ticket["category"],
            "notes": [
                {
                    "id": note["id"],
                    "ticket_id": note["ticket_id"],
                    "author_id": note["author_id"],
                    "author_username": note["author_username"],
                    "note_type": note["note_type"],
                    "body": note["body"],
                    "created_at": note["created_at"],
                }
                for note in notes
            ],
        }
    }), 200

@tickets_bp.post("/tickets/<int:ticket_id>/notes")
def add_ticket_note(ticket_id):
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
    
    ticket = db.execute(
        """
        SELECT id, requester_id, assigned_resolver_id
        FROM tickets
        WHERE id = ?
        """,
        (ticket_id,)
    ).fetchone()

    if ticket is None:
        return jsonify({"error": "Ticket not found"}), 404
    
    if user["role"] == "requester" and ticket["requester_id"] != user["id"]:
        return jsonify({"error": "Forbidden"}), 403
    
    if user["role"] == "resolver" and ticket["assigned_resolver_id"] != user["id"]:
        return jsonify({"error": "Forbidden"}), 403
    
    data = request.get_json() or {}

    body = data.get("body")

    if body is None or body.strip() == "":
        return jsonify({"error": "Note body is required"}), 400
    
    body = body.strip()

    note_type = "requester_note" if user["role"] == "requester" else "resolver_note"

    note_cursor = db.execute(
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
            user["id"],
            note_type,
            body,
        )
    )

    db.commit()

    note_id = note_cursor.lastrowid

    note = db.execute(
        """
        SELECT 
            ticket_notes.id,
            ticket_notes.ticket_id,
            ticket_notes.author_id,
            users.username AS author_username,
            ticket_notes.note_type,
            ticket_notes.body,
            ticket_notes.created_at
        FROM ticket_notes
        JOIN users ON users.id = ticket_notes.author_id
        WHERE ticket_notes.id = ?
        """,
        (note_id,)
    ).fetchone()

    return jsonify({
        "note": {
            "id": note["id"],
            "ticket_id": note["ticket_id"],
            "author_id": note["author_id"],
            "author_username": note["author_username"],
            "note_type": note["note_type"],
            "body": note["body"],
            "created_at": note["created_at"],
        }
    }), 201

@tickets_bp.patch("/tickets/<int:ticket_id>/status")
def update_ticket_status(ticket_id):
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
    
    if user["role"] != "resolver":
        return jsonify({"error": "Forbidden"}), 403
    
    ticket = db.execute(
        """
        SELECT id, status, assigned_resolver_id
        FROM tickets
        WHERE id = ?
        """,
        (ticket_id,)
    ).fetchone()

    if ticket is None:
        return jsonify({"error": "Ticket not found"}), 404
    
    if ticket["assigned_resolver_id"] != user["id"]:
        return jsonify({"error": "Forbidden"}), 403
    
    data = request.get_json() or {}
    new_status = data.get("status")

    allowed_statuses = {"open", "in_progress", "resolved"}

    if new_status not in allowed_statuses:
        return jsonify({"error": "Invalid status"}), 400
    
    if new_status == ticket["status"]:
        return jsonify({
            "ticket": {
                "id": ticket["id"],
                "status": ticket["status"],
            }
        }), 200

    db.execute(
        """
        UPDATE tickets
        SET status = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """,
        (new_status, ticket_id)
    )

    status_note_body = f"Status changed from {ticket['status']} to {new_status}."

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
            user["id"],
            "status_update",
            status_note_body,
        )
    )

    db.commit()

    updated_ticket = db.execute(
        """
        SELECT id, status
        FROM tickets
        WHERE id = ?
        """,
        (ticket_id,)
    ).fetchone()

    return jsonify({
        "ticket": {
            "id": updated_ticket["id"],
            "status": updated_ticket["status"],
        }
    }), 200
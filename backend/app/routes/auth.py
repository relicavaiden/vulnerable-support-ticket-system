from flask import Blueprint, jsonify, request
from werkzeug.security import check_password_hash

from app.db import get_db


auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

@auth_bp.post("/login")
def login():
    data = request.get_json()

    username = data.get("username")
    password = data.get("password")

    db = get_db()
    user = db.execute(
        "SELECT id, username, password_hash, role FROM users WHERE username = ?",
        (username,)
    ).fetchone()

    if user is None:
        return jsonify({"error": "Invalid username or password"}), 401

    if not check_password_hash(user["password_hash"], password):
        return jsonify({"error": "Invalid username or password"}), 401
        
    return jsonify({
            "user": {
                "id": user["id"],
                "username": user["username"],
                "role": user["role"],
            }
        }), 200
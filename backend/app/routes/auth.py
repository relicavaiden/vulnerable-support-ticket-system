from flask import Blueprint, jsonify, request, session
from werkzeug.security import check_password_hash
from datetime import datetime



from app.db import get_db
from app.rate_limit import (
    get_rate_limit,
    is_rate_limit_blocked,
    record_and_apply_rate_limit,
    reset_rate_limit,
)


auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

@auth_bp.post("/login")
def login():
    data = request.get_json() or {}
    current_time = datetime.now()
    source_ip = request.remote_addr

    ip_record = get_rate_limit(
        "ip",
        source_ip,
    )

    if (
        ip_record is not None
        and is_rate_limit_blocked(ip_record, current_time)
    ):
        return jsonify({
            "error": "Too many login attempts. Try again later."
        }), 429

    record_and_apply_rate_limit(
        "ip",
        source_ip,
        current_time,
    )

    username = data.get("username")
    password = data.get("password")

    if not isinstance(username, str) or not isinstance(password, str):
        return jsonify({"error": "Invalid username or password"}), 401

    pair_key = f"{source_ip}:{username}"

    pair_record = get_rate_limit(
        "ip_username",
        pair_key,
    )

    if (
        pair_record is not None
        and is_rate_limit_blocked(pair_record, current_time)
    ):
        return jsonify({
            "error": "Too many login attempts. Try again later."
        }), 429

    db = get_db()
    user = db.execute(
        "SELECT id, username, password_hash, role FROM users WHERE username = ?",
        (username,)
    ).fetchone()

    credentials_invalid = (
        user is None
        or not check_password_hash(user["password_hash"], password)
    )

    if credentials_invalid:
        record_and_apply_rate_limit(
            "ip_username",
            pair_key,
            current_time,
        )
    
        return jsonify({
            "error": "Invalid username or password"
        }), 401

    reset_rate_limit(
        "ip_username",
        pair_key,
    )
    
    session["user_id"] = user["id"]
        
    return jsonify({
            "user": {
                "id": user["id"],
                "username": user["username"],
                "role": user["role"],
            }
        }), 200

@auth_bp.get("/me")
def me():
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

    return jsonify({
        "user": {
            "id": user["id"],
            "username": user["username"],
            "role": user["role"]
        }
    }), 200

@auth_bp.post("/logout")
def logout():
    session.clear()

    return jsonify({"message": "Logged out successfully"}), 200
from functools import wraps
from flask import jsonify, session

from .user_sessions import validate_user_session

def require_authenticated_session(view_function):

    @wraps(view_function)
    def wrapped_view(*args, **kwargs):
        user_id = session.get("user_id")
        session_id = session.get("session_id")
        
        if not validate_user_session(
            user_id,
            session_id,
        ):
            return jsonify({"error": "Not authenticated"}), 401

        return view_function(*args, **kwargs)

    return wrapped_view
from app.db import get_db
from app.seed import seed_db
from datetime import datetime

USER_SESSION_MAX_LIFETIME_SECONDS = 4 * 60 * 60

def create_user_session(user_id, session_id):

    db = get_db()

    db.execute(
        """
        INSERT INTO user_sessions (
        user_id,
        session_id
        )
        VALUES(?, ?)
        """,
        (
            user_id,
            session_id,
        ),
    )

    db.commit()

def get_user_session(session_id):
    db = get_db()

    return db.execute(
        """
        SELECT id, session_id, user_id, created_at, revoked_at
        FROM user_sessions
        WHERE session_id = ?
        """,
        (session_id,),
    ).fetchone()

def revoke_user_session(session_id):
    db = get_db()

    db.execute(
        """
        UPDATE user_sessions
        SET revoked_at = CURRENT_TIMESTAMP
        WHERE session_id = ?
        """,
        (session_id,),
    )

    db.commit()

def is_user_session_active(session_id):
    session_info = get_user_session(session_id)

    if session_info is None:
        return False

    if session_info["revoked_at"] is not None:
        return False

    return True

def validate_user_session(user_id, session_id):

    if user_id is None:
        return False

    if session_id is None:
        return False

    session_info = get_user_session(session_id)

    if session_info is None:
        return False

    if session_info["revoked_at"] is not None:
        return False

    if session_info["user_id"] != user_id:
        return False

    current_time = datetime.now()

    if has_user_session_expired(session_info, current_time):
        return False

    return True

def has_user_session_expired(session_info, current_time):

    created_at = datetime.fromisoformat(session_info["created_at"])

    elapsed = current_time - created_at

    return elapsed.total_seconds() >= USER_SESSION_MAX_LIFETIME_SECONDS
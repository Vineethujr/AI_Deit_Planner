"""
Authentication utilities.

- Passwords are hashed with werkzeug's secure hashing (never stored in plain text).
- Sessions are represented as stateless JWTs (JSON Web Tokens) signed with a
  server-side secret (JWT_SECRET, from environment variables).
- `require_auth` is a decorator that protects routes: it validates the
  Authorization header and injects the authenticated user_id into the view,
  which is how we guarantee one user can never read another user's data
  through normal API calls (see routes for the actual per-user filtering).
"""

from functools import wraps

import jwt
from flask import current_app, jsonify, request


def create_token(user_id: str) -> str:
    import datetime

    now = datetime.datetime.now(datetime.timezone.utc)
    payload = {
        "sub": user_id,
        "iat": now,
        "exp": now + datetime.timedelta(hours=current_app.config["JWT_EXPIRES_HOURS"]),
    }
    return jwt.encode(payload, current_app.config["JWT_SECRET"], algorithm="HS256")


def decode_token(token: str):
    return jwt.decode(token, current_app.config["JWT_SECRET"], algorithms=["HS256"])


def require_auth(view_func):
    """Decorator: requires a valid 'Authorization: Bearer <token>' header.
    On success, passes `user_id` as the first argument to the wrapped view."""

    @wraps(view_func)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or malformed Authorization header."}), 401
        token = auth_header.split(" ", 1)[1]
        try:
            payload = decode_token(token)
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired. Please log in again."}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid authentication token."}), 401

        return view_func(payload["sub"], *args, **kwargs)

    return wrapper

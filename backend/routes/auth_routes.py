from flask import Blueprint, jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from cloud import database_service as db
from backend.utils.auth_utils import create_token, require_auth
from backend.utils.validators import validate_registration

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/register")
def register():
    data = request.get_json(silent=True) or {}
    errors = validate_registration(data)
    if errors:
        return jsonify({"error": "Validation failed.", "details": errors}), 400

    if db.get_user_by_email(data["email"]):
        return jsonify({"error": "An account with this email already exists."}), 409

    password_hash = generate_password_hash(data["password"])
    user_id = db.create_user(data["name"].strip(), data["email"].lower().strip(), password_hash)
    token = create_token(user_id)
    return jsonify({"message": "Registration successful.", "token": token, "user_id": user_id}), 201


@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").lower().strip()
    password = data.get("password") or ""

    user = db.get_user_by_email(email)
    if not user or not check_password_hash(user["password_hash"], password):
        return jsonify({"error": "Invalid email or password."}), 401

    token = create_token(user["user_id"])
    return jsonify({"message": "Login successful.", "token": token, "user_id": user["user_id"]}), 200


@auth_bp.post("/logout")
@require_auth
def logout(user_id):
    # JWTs are stateless, so "logout" is a client-side action (discard the
    # token). This endpoint exists for a clean API contract and to make
    # server-side token revocation (e.g. a denylist) easy to add later.
    return jsonify({"message": "Logged out successfully."}), 200

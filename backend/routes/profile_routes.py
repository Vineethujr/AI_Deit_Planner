import json
from flask import Blueprint, jsonify, request

from cloud import database_service as db
from backend.utils.auth_utils import require_auth
from backend.utils.validators import validate_profile

profile_bp = Blueprint("profile", __name__)


def _serialize_user(user: dict) -> dict:
    safe = {k: v for k, v in user.items() if k != "password_hash"}
    for field in ("allergies", "cuisines"):
        try:
            safe[field] = json.loads(safe.get(field) or "[]")
        except (TypeError, json.JSONDecodeError):
            safe[field] = []
    return safe


@profile_bp.get("/profile")
@require_auth
def get_profile(user_id):
    user = db.get_user_by_id(user_id)
    if not user:
        return jsonify({"error": "User not found."}), 404
    return jsonify(_serialize_user(user)), 200


@profile_bp.put("/profile")
@require_auth
def update_profile(user_id):
    data = request.get_json(silent=True) or {}
    errors = validate_profile(data)
    if errors:
        return jsonify({"error": "Validation failed.", "details": errors}), 400

    updated = db.update_profile(user_id, data)
    if not updated:
        return jsonify({"error": "User not found."}), 404
    return jsonify({"message": "Profile updated.", "profile": _serialize_user(updated)}), 200

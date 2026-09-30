import json
from flask import Blueprint, jsonify, request

from cloud import database_service as db
from backend.utils.auth_utils import require_auth
from ai_engine.diet_engine import generate_diet_plan

plan_bp = Blueprint("plans", __name__)


def _profile_dict(user: dict) -> dict:
    return {
        "sex": user.get("sex"),
        "age": user.get("age"),
        "height_cm": user.get("height_cm"),
        "weight_kg": user.get("weight_kg"),
        "activity_level": user.get("activity_level") or "sedentary",
        "goal": user.get("goal") or "maintenance",
        "dietary_preference": user.get("dietary_preference") or "vegetarian",
        "allergies": json.loads(user.get("allergies") or "[]"),
        "cuisines": json.loads(user.get("cuisines") or "[]"),
    }


@plan_bp.post("/generate-plan")
@require_auth
def generate_plan(user_id):
    user = db.get_user_by_id(user_id)
    if not user:
        return jsonify({"error": "User not found."}), 404
    if not user.get("height_cm") or not user.get("weight_kg") or not user.get("age"):
        return jsonify({
            "error": "Please complete your profile (age, height, weight) before generating a plan."
        }), 400

    # Allow one-off overrides from the request body (e.g. a different goal
    # for this specific plan) without permanently changing the saved profile.
    overrides = request.get_json(silent=True) or {}
    profile = {**_profile_dict(user), **overrides}

    try:
        plan = generate_diet_plan(profile)
    except Exception as exc:  # noqa: BLE001
        return jsonify({"error": "Failed to generate plan.", "details": str(exc)}), 500

    plan_id = db.create_plan(user_id, plan)
    plan["plan_id"] = plan_id
    return jsonify(plan), 201


@plan_bp.get("/plans")
@require_auth
def list_plans(user_id):
    return jsonify({"plans": db.list_plans(user_id)}), 200


@plan_bp.get("/plans/<plan_id>")
@require_auth
def get_plan(user_id, plan_id):
    plan = db.get_plan(user_id, plan_id)
    if not plan:
        return jsonify({"error": "Plan not found."}), 404
    return jsonify(plan), 200


@plan_bp.delete("/plans/<plan_id>")
@require_auth
def delete_plan(user_id, plan_id):
    deleted = db.delete_plan(user_id, plan_id)
    if not deleted:
        return jsonify({"error": "Plan not found."}), 404
    return jsonify({"message": "Plan deleted."}), 200

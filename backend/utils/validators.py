"""Simple, dependency-free input validators for the demo API."""

import re

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

VALID_ACTIVITY_LEVELS = {"sedentary", "light", "moderate", "active", "very_active"}
VALID_GOALS = {"weight_loss", "weight_gain", "maintenance"}
VALID_DIET_PREFS = {"vegan", "vegetarian", "non-vegetarian"}


def validate_registration(data: dict):
    errors = []
    if not data.get("name") or not str(data["name"]).strip():
        errors.append("name is required.")
    email = data.get("email", "")
    if not email or not EMAIL_RE.match(email):
        errors.append("A valid email is required.")
    password = data.get("password", "")
    if not password or len(password) < 8:
        errors.append("password must be at least 8 characters.")
    return errors


def validate_profile(data: dict):
    errors = []
    if "age" in data and not (0 < float(data.get("age") or 0) < 120):
        errors.append("age must be a realistic number.")
    if "height_cm" in data and not (50 <= float(data.get("height_cm") or 0) <= 260):
        errors.append("height_cm must be between 50 and 260.")
    if "weight_kg" in data and not (20 <= float(data.get("weight_kg") or 0) <= 400):
        errors.append("weight_kg must be between 20 and 400.")
    if data.get("activity_level") and data["activity_level"] not in VALID_ACTIVITY_LEVELS:
        errors.append(f"activity_level must be one of {sorted(VALID_ACTIVITY_LEVELS)}.")
    if data.get("goal") and data["goal"] not in VALID_GOALS:
        errors.append(f"goal must be one of {sorted(VALID_GOALS)}.")
    if data.get("dietary_preference") and data["dietary_preference"] not in VALID_DIET_PREFS:
        errors.append(f"dietary_preference must be one of {sorted(VALID_DIET_PREFS)}.")
    return errors

"""
AI Diet Recommendation Engine
==============================
Educational / general-wellness diet plan generator. This is NOT medical or
clinical nutrition advice.

Two layers, matching the project spec:
  - VERSION A: Rule-based recommendation engine (always available, no
    external dependency, deterministic, explainable).
  - VERSION B: Optional external AI API call. If the AI_API_KEY environment
    variable is not set, or the call fails/times out/returns invalid JSON,
    the engine automatically falls back to VERSION A. This keeps the
    project fully executable without any paid API key.

Nothing here should ever be treated as medical or clinical nutrition advice.
Every generated plan is labelled as an educational/general wellness example.
"""

import json
import math
import os
import random
from pathlib import Path

FOOD_DATA_PATH = Path(__file__).parent / "food_data.json"

with open(FOOD_DATA_PATH, "r") as f:
    _CATALOG = json.load(f)["foods"]

DISCLAIMER = (
    "This plan is an educational / general wellness example generated from "
    "demo data. It is not medical or clinical nutrition advice. Consult a "
    "qualified professional for individual dietary guidance."
)

# ---------------------------------------------------------------------------
# Step 1: Convert profile inputs into calorie / macro targets
# (Mifflin-St Jeor BMR + activity multiplier + goal adjustment)
# ---------------------------------------------------------------------------

_ACTIVITY_MULTIPLIERS = {
    "sedentary": 1.2,
    "light": 1.375,
    "moderate": 1.55,
    "active": 1.725,
    "very_active": 1.9,
}

_GOAL_DELTA = {
    "weight_loss": -0.15,
    "weight_gain": 0.15,
    "maintenance": 0.0,
}


def compute_targets(profile: dict) -> dict:
    """Compute BMR, TDEE, target calories, and macro split (grams)."""
    sex = (profile.get("sex") or "female").lower()
    weight_kg = float(profile.get("weight_kg", 65))
    height_cm = float(profile.get("height_cm", 165))
    age = float(profile.get("age", 25))
    activity_level = profile.get("activity_level", "sedentary")
    goal = profile.get("goal", "maintenance")

    sex_offset = 5 if sex == "male" else -161
    bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + sex_offset
    multiplier = _ACTIVITY_MULTIPLIERS.get(activity_level, 1.2)
    tdee = bmr * multiplier
    delta = _GOAL_DELTA.get(goal, 0.0)
    target_cal = tdee * (1 + delta)

    # Default macro split: 30% protein, 40% carbs, 30% fat
    protein_g = round((0.30 * target_cal) / 4)
    carbs_g = round((0.40 * target_cal) / 4)
    fat_g = round((0.30 * target_cal) / 9)

    return {
        "bmr": round(bmr),
        "tdee": round(tdee),
        "target_calories": round(target_cal),
        "macros": {"protein_g": protein_g, "carbs_g": carbs_g, "fat_g": fat_g},
    }


# ---------------------------------------------------------------------------
# VERSION A: Rule-based meal plan generator
# ---------------------------------------------------------------------------

def _filter_catalog(diet_pref: str, allergies: list, meal: str, cuisine_pref: str = "general"):
    diet_pref = (diet_pref or "vegetarian").lower()
    allergies = [a.lower() for a in (allergies or [])]

    def allowed(food):
        if meal not in food["meal"]:
            return False
        tags = food["tags"]
        if diet_pref == "vegan" and "vegan" not in tags:
            return False
        if diet_pref == "vegetarian" and "vegan" not in tags and "vegetarian" not in tags:
            return False
        # non-vegetarian diet allows everything
        if any(a in food["id"] or a in food["name"].lower() for a in allergies):
            return False
        return True

    candidates = [f for f in _CATALOG if allowed(f)]
    if not candidates:
        # relax cuisine constraint before giving up
        candidates = [f for f in _CATALOG if meal in f["meal"]]
    # Prefer requested cuisine when possible, else fall back to any match
    preferred = [f for f in candidates if cuisine_pref in f.get("cuisine", [])]
    return preferred or candidates


def _portion_for_target(food: dict, target_kcal: float) -> dict:
    """Pick a sensible gram amount (rounded to nearest 10g, capped) for one
    food item so that it contributes roughly `target_kcal` calories."""
    per100_kcal = max(food["per100"]["kcal"], 1)
    grams = (target_kcal / per100_kcal) * 100
    grams = max(30, min(round(grams / 10) * 10, 400))
    factor = grams / 100.0
    return {
        "food_id": food["id"],
        "name": food["name"],
        "grams": grams,
        "kcal": round(food["per100"]["kcal"] * factor),
        "protein_g": round(food["per100"]["protein"] * factor, 1),
        "carbs_g": round(food["per100"]["carbs"] * factor, 1),
        "fat_g": round(food["per100"]["fat"] * factor, 1),
    }


# Approximate share of daily calories per meal slot
_MEAL_SHARE = {"breakfast": 0.25, "lunch": 0.35, "snack": 0.10, "dinner": 0.30}


def generate_plan_rule_based(profile: dict, targets: dict, seed: int = None) -> dict:
    rng = random.Random(seed)
    diet_pref = profile.get("dietary_preference", "vegetarian")
    allergies = profile.get("allergies", [])
    cuisine_pref = (profile.get("cuisines") or ["general"])[0].lower()
    target_cal = targets["target_calories"]

    meals = {}
    total = {"kcal": 0, "protein_g": 0.0, "carbs_g": 0.0, "fat_g": 0.0}
    for slot, share in _MEAL_SHARE.items():
        candidates = _filter_catalog(diet_pref, allergies, slot, cuisine_pref)
        food = rng.choice(candidates) if candidates else None
        if food is None:
            meals[slot] = []
            continue
        item = _portion_for_target(food, target_cal * share)
        meals[slot] = [item]
        total["kcal"] += item["kcal"]
        total["protein_g"] += item["protein_g"]
        total["carbs_g"] += item["carbs_g"]
        total["fat_g"] += item["fat_g"]

    return {
        "source": "rule_based",
        "breakfast": meals.get("breakfast", []),
        "lunch": meals.get("lunch", []),
        "snack": meals.get("snack", []),
        "dinner": meals.get("dinner", []),
        "nutrition_summary": {
            "target_calories": target_cal,
            "estimated_calories": round(total["kcal"]),
            "protein_g": round(total["protein_g"], 1),
            "carbs_g": round(total["carbs_g"], 1),
            "fat_g": round(total["fat_g"], 1),
        },
        "hydration_reminder": "Aim for roughly 8 glasses (about 2-2.5 liters) of water across the day.",
        "disclaimer": DISCLAIMER,
    }


# ---------------------------------------------------------------------------
# VERSION B: Optional external AI API call, with fallback to VERSION A
# ---------------------------------------------------------------------------

def _build_prompt(profile: dict, targets: dict) -> str:
    return (
        "You are a general wellness assistant. Based on the following "
        "structured, synthetic user preferences, suggest a one-day meal "
        "plan (breakfast, lunch, snack, dinner) with an approximate "
        "nutrition summary. Respond ONLY with JSON in this shape: "
        '{"breakfast":[{"name":str,"grams":num}], "lunch":[...], '
        '"snack":[...], "dinner":[...], '
        '"nutrition_summary":{"estimated_calories":num,"protein_g":num,'
        '"carbs_g":num,"fat_g":num}}. '
        f"Dietary preference: {profile.get('dietary_preference')}. "
        f"Allergies to avoid: {profile.get('allergies')}. "
        f"Target calories: {targets['target_calories']}. "
        f"Target macros (g): {targets['macros']}. "
        "This is for a general wellness demo, not medical advice."
    )


def generate_plan_ai(profile: dict, targets: dict) -> dict:
    """Attempt to call an external AI API. Falls back to the rule-based
    engine on any failure so the project stays runnable without a paid key.
    """
    api_key = os.environ.get("AI_API_KEY")
    if not api_key:
        plan = generate_plan_rule_based(profile, targets)
        plan["ai_fallback_reason"] = "AI_API_KEY not configured; used rule-based engine."
        return plan

    try:
        import requests  # local import: optional dependency

        prompt = _build_prompt(profile, targets)
        resp = requests.post(
            os.environ.get("AI_API_URL", "https://api.anthropic.com/v1/messages"),
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": "claude-sonnet-4-6",
                "max_tokens": 800,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=8,
        )
        resp.raise_for_status()
        data = resp.json()
        text = "".join(
            block.get("text", "") for block in data.get("content", []) if block.get("type") == "text"
        ).strip()
        text = text.replace("```json", "").replace("```", "").strip()
        parsed = json.loads(text)

        # Basic response validation before trusting it
        required_keys = {"breakfast", "lunch", "snack", "dinner", "nutrition_summary"}
        if not required_keys.issubset(parsed.keys()):
            raise ValueError("AI response missing required keys")

        parsed["source"] = "ai_api"
        parsed["hydration_reminder"] = "Aim for roughly 8 glasses (about 2-2.5 liters) of water across the day."
        parsed["disclaimer"] = DISCLAIMER
        return parsed

    except Exception as exc:  # noqa: BLE001 - intentionally broad: any failure -> fallback
        plan = generate_plan_rule_based(profile, targets)
        plan["ai_fallback_reason"] = f"AI API call failed ({type(exc).__name__}); used rule-based engine."
        return plan


def generate_diet_plan(profile: dict) -> dict:
    """Public entry point used by the backend route."""
    targets = compute_targets(profile)
    plan = generate_plan_ai(profile, targets)
    plan["targets"] = targets
    return plan

"""
Automated tests for the Diet Planner backend.

Run with:
    pytest tests/ -v

Each test corresponds to a row in docs/TESTING.md's test-case table.
Uses a temporary SQLite DB and storage folder per test session so tests
never touch real project data.
"""

import io
import os
import sys
import tempfile

import pytest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture()
def client(monkeypatch, tmp_path):
    # Point the cloud services at a throwaway temp directory BEFORE the app
    # (and therefore the database module) is imported/initialized.
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "test_app.db"))
    monkeypatch.setenv("STORAGE_ROOT", str(tmp_path / "storage_bucket"))
    monkeypatch.setenv("JWT_SECRET", "test-secret")
    monkeypatch.setenv("AI_API_KEY", "")  # force rule-based fallback

    import importlib
    import cloud.database_service as database_service
    importlib.reload(database_service)

    from backend.app import create_app
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def _register(client, email="alice@example.com", password="password123", name="Alice"):
    return client.post("/api/register", json={"name": name, "email": email, "password": password})


def _login(client, email="alice@example.com", password="password123"):
    return client.post("/api/login", json={"email": email, "password": password})


def _auth_header(token):
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------------------------
# TC01 - TC02: Registration
# ---------------------------------------------------------------------------

def test_tc01_new_user_registration_succeeds(client):
    resp = _register(client)
    assert resp.status_code == 201
    assert "token" in resp.get_json()


def test_tc02_existing_email_registration_rejected(client):
    _register(client)
    resp = _register(client)  # same email again
    assert resp.status_code == 409


# ---------------------------------------------------------------------------
# TC03 - TC04: Login
# ---------------------------------------------------------------------------

def test_tc03_valid_login_succeeds(client):
    _register(client)
    resp = _login(client)
    assert resp.status_code == 200
    assert "token" in resp.get_json()


def test_tc04_invalid_login_rejected(client):
    _register(client)
    resp = _login(client, password="wrong-password")
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# TC05: Unauthorized dashboard/profile access
# ---------------------------------------------------------------------------

def test_tc05_unauthorized_profile_access_rejected(client):
    resp = client.get("/api/profile")
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# TC06: Profile creation/update
# ---------------------------------------------------------------------------

def test_tc06_profile_update_succeeds(client):
    token = _register(client).get_json()["token"]
    resp = client.put(
        "/api/profile",
        json={
            "age": 25, "height_cm": 165, "weight_kg": 60, "sex": "female",
            "activity_level": "moderate", "goal": "weight_loss",
            "dietary_preference": "vegetarian", "allergies": ["nuts"],
        },
        headers=_auth_header(token),
    )
    assert resp.status_code == 200
    assert resp.get_json()["profile"]["dietary_preference"] == "vegetarian"


def test_tc06b_profile_update_rejects_invalid_data(client):
    token = _register(client).get_json()["token"]
    resp = client.put("/api/profile", json={"age": 999}, headers=_auth_header(token))
    assert resp.status_code == 400


# ---------------------------------------------------------------------------
# TC07 - TC10: Diet plan generation (incl. vegetarian/vegan/goal variants)
# ---------------------------------------------------------------------------

def _complete_profile(client, token, **overrides):
    base = {
        "age": 28, "height_cm": 170, "weight_kg": 70, "sex": "male",
        "activity_level": "moderate", "goal": "maintenance",
        "dietary_preference": "vegetarian",
    }
    base.update(overrides)
    return client.put("/api/profile", json=base, headers=_auth_header(token))


def test_tc07_diet_plan_generation_succeeds(client):
    token = _register(client).get_json()["token"]
    _complete_profile(client, token)
    resp = client.post("/api/generate-plan", json={}, headers=_auth_header(token))
    assert resp.status_code == 201
    body = resp.get_json()
    assert set(["breakfast", "lunch", "snack", "dinner", "nutrition_summary", "disclaimer"]).issubset(body)
    assert "plan_id" in body


def test_tc08_vegetarian_preference_respected(client):
    token = _register(client).get_json()["token"]
    _complete_profile(client, token, dietary_preference="vegetarian")
    resp = client.post("/api/generate-plan", json={}, headers=_auth_header(token))
    body = resp.get_json()
    all_items = body["breakfast"] + body["lunch"] + body["snack"] + body["dinner"]
    non_veg_names = {"grilled chicken breast", "grilled fish"}
    assert all(item["name"].lower() not in non_veg_names for item in all_items)


def test_tc09_vegan_preference_respected(client):
    token = _register(client).get_json()["token"]
    _complete_profile(client, token, dietary_preference="vegan")
    resp = client.post("/api/generate-plan", json={}, headers=_auth_header(token))
    body = resp.get_json()
    all_items = body["breakfast"] + body["lunch"] + body["snack"] + body["dinner"]
    non_vegan_names = {"paneer (cottage cheese)", "greek yogurt", "boiled egg"}
    assert all(item["name"].lower() not in non_vegan_names for item in all_items)


def test_tc10_different_goal_changes_target_calories(client):
    token = _register(client).get_json()["token"]
    _complete_profile(client, token, goal="weight_loss")
    resp_loss = client.post("/api/generate-plan", json={}, headers=_auth_header(token)).get_json()

    _complete_profile(client, token, goal="weight_gain")
    resp_gain = client.post("/api/generate-plan", json={}, headers=_auth_header(token)).get_json()

    assert resp_loss["targets"]["target_calories"] < resp_gain["targets"]["target_calories"]


def test_tc11_generate_plan_without_profile_rejected(client):
    token = _register(client, email="noprofile@example.com").get_json()["token"]
    resp = client.post("/api/generate-plan", json={}, headers=_auth_header(token))
    assert resp.status_code == 400


# ---------------------------------------------------------------------------
# TC12: AI API failure -> rule-based fallback (simulated via unset AI_API_KEY)
# ---------------------------------------------------------------------------

def test_tc12_ai_fallback_used_when_no_api_key(client):
    token = _register(client).get_json()["token"]
    _complete_profile(client, token)
    resp = client.post("/api/generate-plan", json={}, headers=_auth_header(token))
    body = resp.get_json()
    assert body["source"] == "rule_based"
    assert "ai_fallback_reason" in body


# ---------------------------------------------------------------------------
# TC13 - TC14: Save & retrieve plans
# ---------------------------------------------------------------------------

def test_tc13_save_and_list_plans(client):
    token = _register(client).get_json()["token"]
    _complete_profile(client, token)
    client.post("/api/generate-plan", json={}, headers=_auth_header(token))
    resp = client.get("/api/plans", headers=_auth_header(token))
    assert resp.status_code == 200
    assert len(resp.get_json()["plans"]) == 1


def test_tc14_retrieve_single_plan(client):
    token = _register(client).get_json()["token"]
    _complete_profile(client, token)
    plan_id = client.post("/api/generate-plan", json={}, headers=_auth_header(token)).get_json()["plan_id"]
    resp = client.get(f"/api/plans/{plan_id}", headers=_auth_header(token))
    assert resp.status_code == 200
    assert resp.get_json()["plan_id"] == plan_id


# ---------------------------------------------------------------------------
# TC15 - TC17: File upload / retrieval / invalid file
# ---------------------------------------------------------------------------

def test_tc15_upload_file_succeeds(client):
    token = _register(client).get_json()["token"]
    data = {"file": (io.BytesIO(b"fake image bytes"), "meal.png")}
    resp = client.post(
        "/api/upload", data=data, headers=_auth_header(token), content_type="multipart/form-data"
    )
    assert resp.status_code == 201


def test_tc16_retrieve_uploaded_file(client):
    token = _register(client).get_json()["token"]
    data = {"file": (io.BytesIO(b"fake image bytes"), "meal.png")}
    file_id = client.post(
        "/api/upload", data=data, headers=_auth_header(token), content_type="multipart/form-data"
    ).get_json()["file_id"]

    resp = client.get(f"/api/files/{file_id}", headers=_auth_header(token))
    assert resp.status_code == 200
    assert resp.get_json()["filename"] == "meal.png"


def test_tc17_invalid_file_type_rejected(client):
    token = _register(client).get_json()["token"]
    data = {"file": (io.BytesIO(b"malicious"), "script.exe")}
    resp = client.post(
        "/api/upload", data=data, headers=_auth_header(token), content_type="multipart/form-data"
    )
    assert resp.status_code == 400


# ---------------------------------------------------------------------------
# TC18: User isolation — User A cannot retrieve User B's data
# ---------------------------------------------------------------------------

def test_tc18_user_isolation_enforced(client):
    token_a = _register(client, email="a@example.com").get_json()["token"]
    _complete_profile(client, token_a)
    plan_id = client.post("/api/generate-plan", json={}, headers=_auth_header(token_a)).get_json()["plan_id"]

    token_b = _register(client, email="b@example.com").get_json()["token"]
    resp = client.get(f"/api/plans/{plan_id}", headers=_auth_header(token_b))
    assert resp.status_code == 404  # User B cannot see User A's plan


# ---------------------------------------------------------------------------
# TC19: Logout
# ---------------------------------------------------------------------------

def test_tc19_logout_succeeds(client):
    token = _register(client).get_json()["token"]
    resp = client.post("/api/logout", headers=_auth_header(token))
    assert resp.status_code == 200


# ---------------------------------------------------------------------------
# TC20: Health check (stands in for "cloud/database availability" check)
# ---------------------------------------------------------------------------

def test_tc20_health_check(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ok"

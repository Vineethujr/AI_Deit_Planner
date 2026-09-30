"""
Cloud Database Service (abstraction layer)
===========================================
This module is the ONLY place in the codebase that talks to the database.
Every route/service calls functions here instead of writing raw SQL, so the
underlying "cloud database" implementation can be swapped later (for
example, for Firestore or a managed Postgres instance) without touching
any routes.

Local/free-tier implementation: SQLite file on disk (simulates a managed
cloud database for demo purposes, per the project's "local/simulated
alternative" requirement).

Schema mirrors the spec's collections:
  USERS        -> users
  (profile is stored as columns on users, matching /users/{uid}/profile)
  DIET_PLANS   -> plans
  USER_FILES   -> files
"""

import os
import sqlite3
import time
import uuid
from contextlib import contextmanager

DB_PATH = os.environ.get("DATABASE_PATH", os.path.join(os.path.dirname(__file__), "..", "data", "app.db"))


def _ensure_dir():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)


@contextmanager
def get_conn():
    _ensure_dir()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    """Create tables if they do not already exist. Safe to call on every
    backend startup (idempotent), which mirrors how managed cloud databases
    are typically migrated."""
    with get_conn() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                age INTEGER,
                height_cm REAL,
                weight_kg REAL,
                sex TEXT,
                activity_level TEXT,
                dietary_preference TEXT,
                goal TEXT,
                allergies TEXT,       -- JSON-encoded list
                cuisines TEXT,        -- JSON-encoded list
                created_at REAL NOT NULL
            );

            CREATE TABLE IF NOT EXISTS plans (
                plan_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                breakfast TEXT,        -- JSON
                lunch TEXT,            -- JSON
                snack TEXT,            -- JSON
                dinner TEXT,           -- JSON
                nutrition_summary TEXT,-- JSON
                targets TEXT,          -- JSON
                source TEXT,
                disclaimer TEXT,
                created_at REAL NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS files (
                file_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                filename TEXT NOT NULL,
                storage_path TEXT NOT NULL,
                content_type TEXT,
                size_bytes INTEGER,
                uploaded_at REAL NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            );
            """
        )


# ---------------------------------------------------------------------------
# USERS / PROFILE
# ---------------------------------------------------------------------------

def create_user(name, email, password_hash):
    user_id = str(uuid.uuid4())
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO users (user_id, name, email, password_hash, created_at, allergies, cuisines) "
            "VALUES (?, ?, ?, ?, ?, '[]', '[]')",
            (user_id, name, email, password_hash, time.time()),
        )
    return user_id


def get_user_by_email(email):
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        return dict(row) if row else None


def get_user_by_id(user_id):
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()
        return dict(row) if row else None


def update_profile(user_id, fields: dict):
    import json as _json

    allowed_cols = {
        "name", "age", "height_cm", "weight_kg", "sex", "activity_level",
        "dietary_preference", "goal", "allergies", "cuisines",
    }
    updates = {k: v for k, v in fields.items() if k in allowed_cols}
    if not updates:
        return get_user_by_id(user_id)

    if "allergies" in updates and isinstance(updates["allergies"], list):
        updates["allergies"] = _json.dumps(updates["allergies"])
    if "cuisines" in updates and isinstance(updates["cuisines"], list):
        updates["cuisines"] = _json.dumps(updates["cuisines"])

    set_clause = ", ".join(f"{k} = ?" for k in updates)
    values = list(updates.values()) + [user_id]
    with get_conn() as conn:
        conn.execute(f"UPDATE users SET {set_clause} WHERE user_id = ?", values)
    return get_user_by_id(user_id)


# ---------------------------------------------------------------------------
# DIET PLANS
# ---------------------------------------------------------------------------

def create_plan(user_id, plan: dict):
    import json as _json

    plan_id = str(uuid.uuid4())
    with get_conn() as conn:
        conn.execute(
            """INSERT INTO plans
               (plan_id, user_id, breakfast, lunch, snack, dinner,
                nutrition_summary, targets, source, disclaimer, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                plan_id, user_id,
                _json.dumps(plan.get("breakfast", [])),
                _json.dumps(plan.get("lunch", [])),
                _json.dumps(plan.get("snack", [])),
                _json.dumps(plan.get("dinner", [])),
                _json.dumps(plan.get("nutrition_summary", {})),
                _json.dumps(plan.get("targets", {})),
                plan.get("source", "rule_based"),
                plan.get("disclaimer", ""),
                time.time(),
            ),
        )
    return plan_id


def _row_to_plan(row):
    import json as _json

    d = dict(row)
    for key in ("breakfast", "lunch", "snack", "dinner", "nutrition_summary", "targets"):
        d[key] = _json.loads(d[key]) if d[key] else ([] if key != "nutrition_summary" and key != "targets" else {})
    return d


def list_plans(user_id):
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM plans WHERE user_id = ? ORDER BY created_at DESC", (user_id,)
        ).fetchall()
    return [_row_to_plan(r) for r in rows]


def get_plan(user_id, plan_id):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM plans WHERE plan_id = ? AND user_id = ?", (plan_id, user_id)
        ).fetchone()
    return _row_to_plan(row) if row else None


def delete_plan(user_id, plan_id):
    with get_conn() as conn:
        cur = conn.execute(
            "DELETE FROM plans WHERE plan_id = ? AND user_id = ?", (plan_id, user_id)
        )
    return cur.rowcount > 0


# ---------------------------------------------------------------------------
# FILES (metadata only — bytes live in the storage service)
# ---------------------------------------------------------------------------

def create_file_record(user_id, filename, storage_path, content_type, size_bytes):
    file_id = str(uuid.uuid4())
    with get_conn() as conn:
        conn.execute(
            """INSERT INTO files
               (file_id, user_id, filename, storage_path, content_type, size_bytes, uploaded_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (file_id, user_id, filename, storage_path, content_type, size_bytes, time.time()),
        )
    return file_id


def list_files(user_id):
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM files WHERE user_id = ? ORDER BY uploaded_at DESC", (user_id,)
        ).fetchall()
    return [dict(r) for r in rows]


def get_file(user_id, file_id):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM files WHERE file_id = ? AND user_id = ?", (file_id, user_id)
        ).fetchone()
    return dict(row) if row else None


def delete_file_record(user_id, file_id):
    with get_conn() as conn:
        cur = conn.execute(
            "DELETE FROM files WHERE file_id = ? AND user_id = ?", (file_id, user_id)
        )
    return cur.rowcount > 0

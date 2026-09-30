# Architecture

## What is an AI-Powered Personal Diet Planner with Cloud Storage?

**Simple explanation:** an app where you answer a few questions about
yourself (age, height, weight, activity, diet preference, goal), and it
builds you a one-day meal plan with an estimated calorie/macro count. Your
answers and plans are saved to an account so you can log in from any
device and see them again.

**Technical explanation:** a client-server web application. A React
single-page app collects structured profile data and sends it over REST
APIs to a Python backend. The backend authenticates the request, computes
calorie/macro targets from the profile (Mifflin-St Jeor BMR formula), and
either calls an external AI API or a local rule-based engine to build a
meal plan. Structured data (profile, plan, file metadata) is written to a
cloud database; raw files (e.g. an optional meal photo) are written to
cloud object storage. Everything is scoped per authenticated user.

## Why cloud computing for this project

- **Anywhere access / multi-device sync** — the plan is tied to an
  account, not a browser's local storage, so it follows the user.
- **Separation of concerns** — frontend, backend, database, and storage
  can each be deployed, scaled, and monitored independently.
- **Elastic capacity** — a managed database/storage/hosting layer can grow
  with demand instead of a single machine hitting a hard limit.

## Cloud database vs. cloud object storage

| | Cloud Database | Cloud Object Storage |
|---|---|---|
| Stores | Structured rows/documents (profile fields, plan metadata) | Raw files (images, exported PDFs) |
| Queried by | Fields (e.g. `user_id`, `created_at`) | Key/path lookup |
| This project | `cloud/database_service.py` → SQLite locally, Firestore-ready | `cloud/storage_service.py` → local folder locally, Firebase/S3-ready |

## Data flow

```
User
  |
  v
React Frontend (Vite)
  |  fetch() with JWT in Authorization header
  v
REST API (Flask, /api/*)
  |
  |--> Auth middleware (verifies JWT, resolves user_id)
  |
  |--> AI Diet Engine (ai_engine/diet_engine.py)
  |       - computes BMR/TDEE/macro targets
  |       - calls external AI API if AI_API_KEY set
  |       - falls back to rule-based engine on any failure
  |
  |--> Cloud Database Service (cloud/database_service.py)
  |       - users, plans, file metadata
  |
  |--> Cloud Storage Service (cloud/storage_service.py)
          - uploaded file bytes
  |
  v
User Dashboard (renders profile, latest plan, saved plans, files)
```

## System architecture diagram (text form)

```
                     User
                      |
                      v
                  Frontend (React)
                      |
                      v
               Authentication (JWT)
                      |
                      v
                  REST API
                      |
                      v
              Backend Application (Flask)
                      |
      +---------------+----------------+
      |               |                |
      v               v                v
  AI Engine      Cloud Database   Cloud Storage
      |               |                |
      +-------+-------+-------+--------+
              |               |
              v               v
          Diet Plan       Dashboard
```

## Cloud computing concepts demonstrated here

| Concept | Where it appears |
|---|---|
| Client-server architecture | React frontend calls the Flask REST API over HTTP |
| REST API | `backend/routes/*.py` — resource-oriented endpoints, HTTP verbs, status codes |
| Authentication | JWT issued on login, verified by `require_auth` on every protected route |
| Authorization / user isolation | Every query in `database_service.py` filters by `user_id` |
| Cloud database | `cloud/database_service.py` (SQLite locally; swap for Firestore/Cloud SQL) |
| Object storage | `cloud/storage_service.py` (local bucket folder; swap for Firebase Storage/S3) |
| Environment variables / secrets management | `.env` (git-ignored), read via `backend/config.py` |
| Serverless computing | Deployment doc shows a Cloud Functions variant of `generate-plan` |
| Scalability / elasticity | See "Scalability" in README — stateless backend + managed DB + autoscaling |
| Load balancing / API Gateway | Discussed in deployment doc for the AWS/GCP option |
| Logging / monitoring | Flask request logs locally; Cloud Run/Cloud Logging in cloud deployment |
| CI/CD | GitHub Actions example in `docs/DEPLOYMENT.md` |
| SaaS / PaaS / IaaS | SaaS: the finished app itself. PaaS: Cloud Run/Render running our code without managing servers. IaaS: a raw VM alternative, discussed for completeness. |

## Database design

**users** (mirrors `/users/{uid}/profile`)
`user_id` (PK), `name`, `email` (unique), `password_hash`, `age`,
`height_cm`, `weight_kg`, `sex`, `activity_level`, `dietary_preference`,
`goal`, `allergies` (JSON list), `cuisines` (JSON list), `created_at`.

**plans** (`/users/{uid}/plans/{planId}`)
`plan_id` (PK), `user_id` (FK → users), `breakfast`/`lunch`/`snack`/`dinner`
(JSON), `nutrition_summary` (JSON), `targets` (JSON), `source`,
`disclaimer`, `created_at`.

**files** (`/users/{uid}/files`, metadata only — bytes live in storage)
`file_id` (PK), `user_id` (FK → users), `filename`, `storage_path`,
`content_type`, `size_bytes`, `uploaded_at`.

Relationships: one user has many plans and many files (1-to-many via
`user_id`). Every read/write in `database_service.py` takes `user_id` as a
required filter, which is what prevents one user from reading another
user's rows through the normal API — there is no endpoint that returns a
plan or file without also checking `user_id` ownership (see
`tests/test_backend.py::test_tc18_user_isolation_enforced`).

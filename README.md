# AI-Powered Personal Diet Planner with Cloud Storage

A cloud-computing course project: a full-stack web app that turns a short
user profile into a personalized one-day meal plan, with authentication,
a cloud database, cloud object storage, and a documented path to real
cloud deployment.

> **Disclaimer:** This is an educational / general wellness demo. All
> generated diet plans are illustrative examples, not medical or clinical
> nutrition advice. All user data used for testing is synthetic/demo data.

## Overview

- **Frontend**: React (Vite) — registration, login, profile, plan
  generation, saved plans, file uploads, dashboard.
- **Backend**: Flask REST API with JWT authentication.
- **AI engine**: rule-based meal-plan generator (BMR/TDEE/macro math),
  with an optional external-AI-API path that automatically falls back to
  the rule-based engine on any failure — so the project runs with zero
  paid dependencies.
- **Cloud database**: abstracted behind `cloud/database_service.py`
  (SQLite locally; swap in Firestore/Cloud SQL for real cloud use).
- **Cloud object storage**: abstracted behind `cloud/storage_service.py`
  (local folder locally; swap in Firebase Storage/S3 for real cloud use).
- **Tests**: 21 automated pytest cases (see `docs/TESTING.md`).

## Problem statement & objectives

People struggle to plan balanced meals and track calories/macros
consistently. This project demonstrates how a cloud-backed architecture
(auth, database, storage, and a backend API) can deliver a personalized,
always-accessible planning tool — while staying strictly within
"general wellness education," not medical advice.

## Features

- Register / log in / log out (JWT-based sessions)
- Profile: age, height, weight, activity level, dietary preference, goal,
  allergies
- Generate a one-day plan (breakfast/lunch/snack/dinner) with an
  estimated nutrition summary and a hydration reminder
- Save, list, view, and delete past plans
- Upload, list, and delete demo files (cloud object storage)
- Dashboard summarizing goal, preference, latest plan, and files

## Cloud computing concepts demonstrated

See the full table in [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md):
client-server architecture, REST APIs, authentication/authorization,
cloud database vs. object storage, environment variables & secrets
management, serverless-ready design, scalability/elasticity, logging,
and CI/CD.

## Technology stack

| Layer | Choice |
|---|---|
| Frontend | React 18 + Vite, React Router |
| Backend | Python 3.11+, Flask, Flask-CORS |
| Auth | PyJWT + Werkzeug password hashing |
| Database (local/demo) | SQLite, swappable for Firestore/Cloud SQL |
| Object storage (local/demo) | Local filesystem bucket, swappable for Firebase Storage/S3 |
| AI engine | Rule-based (always available) + optional external AI API with fallback |
| Testing | pytest |

Three implementation options (beginner / recommended / advanced) are
compared in `docs/DEPLOYMENT.md`; this repository ships the
**recommended, free-tier-executable** version of that stack.

## Folder structure

```
AI-Personal-Diet-Planner-Cloud/
├── frontend/            React app (pages, components, services, context)
├── backend/              Flask app, routes, config, auth/validation utils
├── ai_engine/            Rule-based + AI-fallback diet recommendation engine
├── cloud/                Database & object-storage abstraction layers
├── tests/                pytest suite (21 automated test cases)
├── docs/                 Architecture, deployment, testing, interview prep
├── sample_data/          Example request/response payloads
├── requirements.txt
├── .env.example
└── .gitignore
```

## Installation & local setup

**Prerequisites**: Python 3.11+, Node.js 18+.

```bash
# 1. Clone / open the project folder
cd AI-Personal-Diet-Planner-Cloud

# 2. Backend: virtual environment + dependencies
python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 3. Configure environment variables
cp .env.example .env
# edit .env if you want to change the JWT secret, ports, etc.
# AI_API_KEY can stay empty — the rule-based engine is used automatically.

# 4. Run the backend
python backend/app.py
# -> http://localhost:5000/api/health should return {"status": "ok"}

# 5. Frontend (in a second terminal)
cd frontend
cp .env.example .env
npm install
npm run dev
# -> http://localhost:5173
```

### Try it out

1. Open the frontend, click **Sign up**, create a demo account.
2. Fill in your **Profile** (age, height, weight, activity, goal, diet
   preference).
3. Go to **Generate Plan** → view your plan → it's auto-saved.
4. Check **Saved Plans** and **Files** (try uploading a small image).
5. Log out and log back in — your data is still there.

## Environment variables

See `.env.example` (backend) and `frontend/.env.example`. Nothing is
hardcoded — API keys, the JWT secret, and CORS origins are all read from
the environment. Never commit a real `.env` file.

## Running the tests

```bash
pytest tests/ -v
```

21/21 tests pass, covering registration, login, authorization/user
isolation, profile validation, plan generation across dietary
preferences and goals, the AI-fallback path, and file upload/validation.
Full test-case table: [`docs/TESTING.md`](docs/TESTING.md).

## Cloud deployment

Three deployment paths — free-tier, Firebase-based, and AWS/GCP — are
documented with exact commands in
[`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md), along with a local-vs-cloud
comparison table and a sample GitHub Actions CI/CD workflow.

## Security

- Passwords hashed with Werkzeug's `generate_password_hash` — never
  stored or logged in plain text.
- Stateless JWT sessions, verified on every protected route.
- Per-user data isolation enforced at the database-query level (every
  read/write filters by `user_id`), verified by an automated test.
- Secrets via environment variables only; `.env` is git-ignored.
- Uploaded file type/size validated server-side before writing to
  storage.
- CORS restricted to configured origins, not left wide open.

In a production system you would add on top of this: HTTPS/TLS
termination, encryption at rest for the database and bucket, rate
limiting, structured logging shipped to a monitoring service, and
periodic backups.

## Scalability

- **10 users**: current architecture (single backend process, SQLite,
  local file storage) handles this comfortably.
- **1,000 users**: move to a managed database (handles concurrent writes
  safely) and a real object storage bucket; run 2–3 backend instances
  behind a load balancer.
- **100,000 users**: autoscaling backend instances, a managed database
  with read replicas, a CDN in front of the static frontend, caching for
  hot reads (e.g. the food catalog), and a queue for any background/batch
  work (e.g. weekly target recalculation).

## Limitations

- The rule-based engine picks one food per meal slot, so estimated
  calories can undershoot the target for some profiles — see
  `docs/TESTING.md`.
- Local SQLite/file storage is for demo/dev only — not concurrent-safe
  or durable enough for real production traffic.
- Diet plans are educational examples only, not medical or clinical
  nutrition advice.

## Future improvements

Multi-item meal composition to hit macro targets more precisely, meal
substitutions and a shopping list, scheduled weekly target adjustment
based on logged intake, push notifications, containerized deployment
with CI/CD, infrastructure-as-code, and stronger observability.

## Learning outcomes

Building this project covered: REST API design, JWT authentication and
per-user authorization, the practical difference between a cloud
database and cloud object storage, writing code against an abstraction
layer so the underlying cloud provider can change without touching
business logic, designing fallback logic for an unreliable external
dependency, and documenting an architecture for both a grader and a
future maintainer.

## Resume, LinkedIn & interview prep

See [`docs/INTERVIEW_PREP.md`](docs/INTERVIEW_PREP.md) for resume
bullets, a LinkedIn project description, technical skills list, and 10
predicted interview questions with answers.

## Author

Student project — Cloud Computing coursework.

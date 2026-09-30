# Deployment

## Local development vs. cloud deployment

| | Local development | Cloud deployment |
|---|---|---|
| Database | SQLite file in `data/app.db` | Managed database (Firestore / Cloud SQL / Supabase) |
| File storage | Local folder `data/storage_bucket/` | Managed object storage (Firebase Storage / S3 / GCS) |
| Backend | `python backend/app.py` on your machine | Container/Function on a managed platform |
| Frontend | `npm run dev` (Vite dev server) | Static build (`npm run build`) served by a CDN/host |
| Secrets | `.env` file (git-ignored) | Platform's secret manager / environment variable UI |
| Scale | Single process, single user in practice | Autoscaled, many concurrent users |

## Approach A — student-friendly / free-tier deployment

This keeps the local architecture (SQLite + local storage) but puts it
online, which is enough to demonstrate cloud hosting, environment
variables, and a public URL without needing paid cloud credentials.

1. **Backend** — deploy to a free-tier host that runs a Python web
   service from a Git repo (e.g. Render, Railway, or a Fly.io free
   instance). Typical steps:
   - Push this repository to GitHub.
   - Create a new "Web Service" pointing at the repo, root directory
     `backend/`, or run command `gunicorn -w 2 -b 0.0.0.0:$PORT backend.app:app`
     from the repo root (`gunicorn` should be added to `requirements.txt`
     for production; the dev server used locally is not for production use).
   - Set environment variables from `.env.example` in the platform's
     dashboard — never commit real values.
   - Note: SQLite + local file storage on most free-tier hosts is
     **ephemeral** (reset on redeploy). This is acceptable for a course
     demo; Approach B replaces it with a managed database and storage
     bucket for anything meant to persist.

2. **Frontend** — deploy the static build to a free static host (e.g.
   Vercel, Netlify, or GitHub Pages):
   ```bash
   cd frontend
   npm install
   npm run build
   # deploy the generated dist/ folder to your chosen static host
   ```
   Set `VITE_API_BASE_URL` to the backend's public URL before building.

3. **Logs / monitoring** — most free-tier hosts show request logs and
   basic CPU/memory graphs in their dashboard; that satisfies "logging and
   monitoring" for a course project.

## Approach B — Firebase-based recommended stack

Matches the spec's "Option B — Recommended" stack: Firebase
Authentication, Firestore, Firebase Storage, and Cloud Functions, with
Firebase Hosting for the frontend.

```bash
npm i -g firebase-tools
firebase login
firebase init            # choose Hosting + Functions + Firestore
```

- Replace `cloud/database_service.py`'s function bodies with Firestore
  reads/writes (the function signatures stay the same, so
  `backend/routes/*.py` does not need to change).
- Replace `cloud/storage_service.py`'s function bodies with Firebase
  Storage `upload_from_string` / `download_as_bytes` calls.
- Deploy:
  ```bash
  cd frontend && npm run build && cd ..
  firebase deploy
  ```
- Firestore security rules should mirror the "one user cannot read
  another user's data" guarantee already enforced in the backend, e.g.:
  ```js
  match /users/{uid}/plans/{planId} {
    allow read, write: if request.auth != null && request.auth.uid == uid;
  }
  ```

## Approach C — AWS / Azure / GCP (advanced)

For a fuller cloud-computing demonstration:

- **Compute**: Cloud Run (GCP) or App Runner (AWS) running the Flask app
  in a container — serverless, autoscaling, pay-per-use.
- **Database**: Cloud SQL / RDS (managed Postgres) instead of SQLite.
- **Object storage**: Google Cloud Storage / S3 bucket.
- **Auth**: Firebase Auth, Cognito, or a self-hosted equivalent of this
  project's JWT scheme.
- **API Gateway**: Cloud Endpoints / API Gateway in front of Cloud Run,
  for rate limiting and request logging at the edge.
- **CI/CD**: a GitHub Actions workflow that runs `pytest`, builds the
  Docker image, and deploys on every push to `main`:

```yaml
# .github/workflows/deploy.yml (illustrative)
name: Deploy
on:
  push:
    branches: [main]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.11" }
      - run: pip install -r requirements.txt
      - run: pytest tests/ -v
  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: echo "build & push container, then deploy to Cloud Run"
```

Sample container build for the Flask backend:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt gunicorn
COPY backend/ backend/
COPY ai_engine/ ai_engine/
COPY cloud/ cloud/
ENV PORT=8080
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:8080", "backend.app:app"]
```

```bash
gcloud builds submit --tag gcr.io/PROJECT_ID/diet-planner-backend
gcloud run deploy diet-planner-backend \
  --image gcr.io/PROJECT_ID/diet-planner-backend \
  --platform managed --region asia-south1 --allow-unauthenticated
```

## Environment variables reference

See `.env.example` at the repo root and `frontend/.env.example`. Never
commit a real `.env` file — it is already listed in `.gitignore`.

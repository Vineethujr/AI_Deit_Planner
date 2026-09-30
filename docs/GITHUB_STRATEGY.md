# GitHub Upload & Proof-Building Strategy

## Repository setup

```bash
git init
git add .
git commit -m "Initialize cloud diet planner project"
git branch -M main
git remote add origin <your-repo-url>
git push -u origin main
```

**Suggested repo name:** `AI-Powered-Personal-Diet-Planner-Cloud`
**Suggested topics:** cloud-computing, artificial-intelligence, python,
flask, react, cloud-storage, rest-api, full-stack, cloud-application

## Day-wise development history

Commit in this order (even if you build it in one sitting, splitting the
commits this way tells an honest, readable story of the build):

| Day | Focus | Files | Commit message | Screenshot to capture |
|---|---|---|---|---|
| 1 | Architecture + repo setup | `README.md`, `docs/ARCHITECTURE.md`, `.gitignore` | "Create cloud application architecture" | Folder structure, architecture diagram |
| 2 | Frontend scaffold | `frontend/` (Vite + routing shell) | "Set up frontend scaffold" | Landing page |
| 3 | Backend REST API skeleton | `backend/app.py`, route files (stubs) | "Implement diet plan REST API skeleton" | Backend running in terminal |
| 4 | Authentication | `backend/routes/auth_routes.py`, `backend/utils/auth_utils.py` | "Add user authentication" | Register/login pages |
| 5 | Cloud database | `cloud/database_service.py` | "Integrate cloud database" | Database record |
| 6 | AI recommendation engine | `ai_engine/` | "Add AI diet recommendation engine" | Diet preference selection |
| 7 | Diet plan generation wired up | `backend/routes/plan_routes.py`, `frontend/src/pages/GeneratePlan.jsx` | "Implement diet plan generation flow" | Generated plan |
| 8 | Cloud storage | `cloud/storage_service.py`, `backend/routes/file_routes.py`, `frontend/src/pages/Files.jsx` | "Add cloud object storage" | File upload UI, storage bucket |
| 9 | Dashboard | `frontend/src/pages/Dashboard.jsx` | "Build user dashboard" | Dashboard |
| 10 | AI fallback + validation hardening | `ai_engine/diet_engine.py`, `backend/utils/validators.py` | "Add AI fallback mechanism and input validation" | — |
| 11 | Testing | `tests/test_backend.py`, `docs/TESTING.md` | "Add application tests" | `pytest -v` output |
| 12 | Deployment | `docs/DEPLOYMENT.md` | "Document and deploy application to cloud" | Deployment dashboard, live app |
| 13 | Documentation polish | `README.md`, `docs/INTERVIEW_PREP.md`, `screenshots/` | "Complete README and documentation" | README preview on GitHub |

Each row's file list is a natural PR/commit boundary — commit as you
finish each row rather than all at once, so the history reflects real
incremental progress.

# Resume, LinkedIn & Interview Preparation

Do not present this as a production healthcare or clinical nutrition
system — it's a course/portfolio project demonstrating cloud-computing
concepts through a diet-planning demo app.

## Resume bullet points

- Built a full-stack cloud application (React, Flask, REST APIs) with JWT
  authentication, a rule-based AI recommendation engine with automatic
  fallback logic, and a database/object-storage abstraction layer ready
  to swap in Firebase or AWS services.
- Designed and enforced per-user data isolation across all API endpoints,
  verified with an automated pytest suite covering authentication,
  authorization, and 20+ functional test cases.
- Documented complete cloud architecture, deployment options (free-tier,
  Firebase, and AWS/GCP), and a GitHub-based development history to
  demonstrate industry-style project delivery.

## Two-line resume description

AI-assisted diet-planning web app with JWT authentication, a REST API
backend, and a cloud database/storage abstraction layer; includes a
rule-based recommendation engine with AI-API fallback and an automated
test suite.

## LinkedIn project description

**AI-Powered Personal Diet Planner with Cloud Storage** — A cloud
computing course project demonstrating a full client-server architecture:
a React frontend, a Flask REST API, JWT-based authentication with
per-user data isolation, a cloud database and object storage layer (built
local-first for free-tier execution, with a clean interface for swapping
in Firebase/AWS), and a rule-based AI diet recommendation engine with
automatic fallback when no external AI service is configured. Covered
with an automated pytest suite and documented deployment paths from
free-tier hosting through to a full AWS/GCP architecture. Educational
project — not medical or clinical nutrition software.

## Technical skills demonstrated

Python (Flask), REST API design, JWT authentication & authorization,
SQLite/relational schema design, cloud storage abstraction, React (hooks,
context, routing), Vite, automated testing (pytest), environment-variable
based secrets management, cloud deployment architecture (Firebase,
Cloud Run/GCP), Git/GitHub workflow.

## Suggested GitHub repository description

"Cloud-based AI-powered personal diet planning application with
authentication, personalized recommendation generation, cloud database
integration, object storage, and scalable deployment architecture."

---

## Interview questions and answers

**1. Explain your project.**
I built a cloud-based web application that generates personalized
diet-plan suggestions from a short user profile — dietary preference,
activity level, and general goal. The React frontend talks to a Python
Flask backend over REST APIs. Profiles and generated plans are stored in
a database, and optional files go into an object storage layer. Everyone
authenticates with a JWT so their data stays isolated from other users.
The recommendation engine can call an external AI API, but I built in a
rule-based fallback so the project runs without needing a paid key.

**2. Why did you use cloud computing for this project?**
Cloud computing lets the app, database, authentication, and storage be
reached from any device instead of living on one machine. It also gives a
clean separation between frontend, backend, and data layers, which makes
the app easier to scale, monitor, and redeploy independently.

**3. What's the difference between cloud database and cloud storage in
your project?**
The database stores structured information — user profiles, plan
metadata, file records — as rows I can query by field. Object storage
holds the raw file bytes themselves, like an uploaded meal photo,
addressed by a storage path rather than queried by field. Using the
right one for each kind of data keeps the architecture efficient.

**4. How does the AI recommendation engine work?**
The backend first computes calorie and macro targets from the user's
profile using the Mifflin-St Jeor BMR formula and an activity multiplier.
Those targets, plus dietary preference and allergies, are passed either
to an external AI API or to a local rule-based engine that picks foods
from a small catalog to approximate the targets. If the AI API isn't
configured or fails for any reason, the code catches that and falls back
to the rule-based engine automatically, so a broken or missing API key
never breaks the app.

**5. How did you secure user data?**
Passwords are hashed, never stored in plain text. Sessions are stateless
JWTs verified on every protected route, and every database query is
filtered by the authenticated user's ID, so one user's API calls simply
cannot return another user's rows — I have an automated test that proves
this directly. Secrets like the JWT signing key and any AI API key are
read from environment variables, never hardcoded, and are excluded from
version control via `.gitignore`.

**6. What is the role of REST APIs in this project?**
REST APIs are the contract between frontend and backend: endpoints like
`POST /generate-plan`, `GET /plans`, and `POST /upload` let the frontend
ask for exactly what it needs without knowing how the backend is
implemented. That separation means I could swap the database or storage
implementation without touching the frontend at all.

**7. What happens if the AI API fails?**
The call is wrapped in a try/except that catches network errors, timeouts,
and invalid/malformed responses. On any of those, the backend logs the
reason and switches to the rule-based engine for that request, so the
user still gets a usable plan instead of an error page.

**8. How would you scale this application if the number of users
increased significantly?**
I'd move the backend to stateless containers behind a load balancer with
autoscaling, replace SQLite with a managed database that handles
concurrent writes, keep files in a horizontally-scaled object storage
bucket, put a CDN in front of the static frontend, add caching for
frequently-read data like the food catalog, and use a queue for anything
slower than a request/response cycle (like a batch weekly recalculation).

**9. How did you test this project?**
I wrote an automated pytest suite covering registration, login, invalid
credentials, unauthorized access, profile validation, plan generation
across dietary preferences and goals, the AI-fallback path, file upload
including invalid file types, and — importantly — that one user cannot
retrieve another user's plans or files. All of that runs against a
temporary database so it never touches real data, and I also walked
through the full flow manually against a live running server.

**10. How can this project be improved further?**
The rule-based engine currently picks one food per meal slot; a v2 could
combine multiple items to hit macro targets more precisely, add a
shopping list, support meal substitutions, and add scheduled recalculation
based on logged intake versus targets. Infrastructure-wise, I'd add CI/CD,
containerize the backend, and move to a managed database and storage
bucket for real persistence in production. Any real dietary/medical
functionality would need professional and regulatory review before use.

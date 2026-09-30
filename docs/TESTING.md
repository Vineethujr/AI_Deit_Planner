# Testing Strategy

Automated tests live in `tests/test_backend.py` (pytest + Flask's test
client, run against a temporary SQLite DB and storage folder — never your
real data). Run them with:

```bash
pytest tests/ -v
```

All 21 automated tests pass as of the last run in this repository.

## Test case table

| Test ID | Scenario | Input | Expected Result | Automated? |
|---|---|---|---|---|
| TC01 | New user registration | Valid name/email/password | 201, token returned | Yes |
| TC02 | Existing email registration | Email already used | 409 conflict | Yes |
| TC03 | Valid login | Correct email/password | 200, token returned | Yes |
| TC04 | Invalid login | Wrong password | 401 unauthorized | Yes |
| TC05 | Unauthorized dashboard access | No/invalid token on `/profile` | 401 unauthorized | Yes |
| TC06 | Profile creation/update | Valid profile fields | 200, profile echoed back | Yes |
| TC06b | Invalid profile data | Age = 999 | 400 validation error | Yes |
| TC07 | Diet plan generation | Complete profile | 201, plan with all meal slots | Yes |
| TC08 | Vegetarian preference | `dietary_preference=vegetarian` | No non-veg items in plan | Yes |
| TC09 | Vegan preference | `dietary_preference=vegan` | No dairy/egg items in plan | Yes |
| TC10 | Different goal | `weight_loss` vs `weight_gain` | Loss target < gain target | Yes |
| TC11 | Generate plan without profile | Missing age/height/weight | 400 "complete your profile" | Yes |
| TC12 | AI API failure / no key | `AI_API_KEY` unset | Falls back to rule-based engine, `source="rule_based"` | Yes |
| TC13 | Save diet plan | Generate a plan | Appears in `GET /plans` | Yes |
| TC14 | Retrieve plan | `GET /plans/{id}` | Correct plan returned | Yes |
| TC15 | Upload file | Valid `.png` under 5 MB | 201, file_id returned | Yes |
| TC16 | Retrieve file | `GET /files/{id}` | Correct filename + base64 content | Yes |
| TC17 | Invalid file | `.exe` extension | 400 rejected | Yes |
| TC18 | User A cannot retrieve User B's data | User B requests User A's plan_id | 404 not found | Yes |
| TC19 | Logout | Valid token | 200 success | Yes |
| TC20 | Cloud/database health check | `GET /api/health` | 200, `status: ok` | Yes |

## Manual / exploratory checks

These were also verified manually against a running local server as part
of building this project (register → login → update profile → generate
plan → upload file → list plans/files):

- Frontend build (`npm run build`) completes with no errors.
- Full register → profile → generate-plan → save → upload → retrieve flow
  works end-to-end over real HTTP requests (not just the test client).
- CORS is scoped to `CORS_ORIGINS` from the environment, not left open.

## Known limitation to be aware of when testing

The rule-based planner picks one food per meal slot and caps portions at
400g, so `estimated_calories` in the nutrition summary can come in below
`target_calories` for some profiles (visible in TC07/TC10 output). This is
expected behavior for the v1 baseline engine, not a bug — see
"Future Improvements" in the README for how a v2 engine would address it
(e.g. allowing multiple items per meal).

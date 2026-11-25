# AGENTS.md

## Layout & entrypoints
- `backend/` is Django 6.1 + DRF/Channels (project config in `backend/config/`); `frontend/` is a Vite/React SPA (`src/main.jsx` → `src/App.jsx`). No root-level build/test runner.
- Python env is the root `venv/`. From `backend/`, use `..\venv\Scripts\python.exe`. Install from `backend/requirements.txt`; the root `requirements.txt` is an older/partial duplicate (missing `redis`, Twisted, etc.).
- `config/settings.py` loads only the root `.env` via `load_dotenv(BASE_DIR.parent / ".env")`, never `backend/.env`. This checkout already has a locally configured `.env` with Postgres credentials; don't overwrite it with `.env.example` (that README step is for fresh clones).
- WebSockets need ASGI/Daphne (`config.asgi:application`), not WSGI. Channel layer is in-memory unless `REDIS_URL` is set; Redis is only needed for multi-process/production.
- Admin is a custom site: `config.admin.SocialConnectAdminConfig` → `config/admin_site.py`, with overrides in `backend/templates/admin/` and `backend/static/admin/`.

## Verification commands (PowerShell)
```powershell
# from backend/
..\venv\Scripts\python.exe manage.py check
..\venv\Scripts\python.exe manage.py makemigrations --check --dry-run
..\venv\Scripts\python.exe manage.py test --keepdb
..\venv\Scripts\python.exe manage.py test social --keepdb
..\venv\Scripts\python.exe manage.py test social.tests.SocialFeatureTests.test_feed_pagination_is_opt_in_and_returns_next_page --keepdb

# from frontend/
npm.cmd run lint
npm.cmd run build
```
- Use `npm.cmd`, not `npm`: `npm` resolves to `npm.ps1`, which this machine's PowerShell execution policy blocks.
- Backend tests use real PostgreSQL; the DB user must be able to create/reuse the test database. `--keepdb` avoids the interactive create prompt that breaks non-interactive shells. Full suite is slow (~6 min per the validation report).
- WebSocket tests are `TransactionTestCase`s using Channels' `WebsocketCommunicator` against `config.asgi.application` (see `backend/chat/tests.py`), not the Django test client.
- There is no `npm test` script or frontend test files despite `vitest`/`jsdom` in devDependencies. Lint + build are the only frontend checks.

## Repo-specific gotchas
- Treat `runtime-validation-report.md`, `PROJECT_COMPLETION_REPORT.md` and `BUG_FIX_REPORT.md` as historical snapshots, not current status. Verify with the commands above rather than trusting their pass/fail claims.
- Frontend API defaults to `http://127.0.0.1:8000/api/`; override with `VITE_API_BASE_URL` and use `VITE_API_ORIGIN` for media/WebSocket origins. Session state is in localStorage (`access`, `refresh`, `user_id`, `username`); route guards only check `access`, and 401 refresh logic lives in `frontend/src/api/axios.js`.
- Stories, group chat, polls, drafts/scheduling, pinning, reposts, reports and hashtags are backend/model features or partially wired; don't assume a finished UI. There is no `/explore` or `/settings` SPA route; the admin dashboard is Django `/admin/`.
- Git: root and `backend/` are separate repos, both with zero commits; everything is untracked, so there is no commit history or `git diff` baseline to consult.

# AGENTS.md (backend)

Django 6.1 + DRF + Channels API (`config/` project; apps: `users`, `posts`, `social`, `chat`, `notifications`). This directory is its own git repo with zero commits — no history/diff baseline. Workspace-wide and frontend notes live in `../AGENTS.md` and `../README.md`.

## Environment / entrypoints
- Use `..\venv\Scripts\python.exe` (Python 3.13, root venv), not a backend-local env. Install from `backend/requirements.txt`; root `requirements.txt` is an older partial duplicate (missing `redis`, Twisted, etc.).
- `config/settings.py` loads `.env` only from the workspace root (`BASE_DIR.parent / ".env"`), never `backend/.env`. That `.env` is already configured locally; don't overwrite it with `.env.example`.
- Postgres is mandatory (no SQLite fallback): `DB_NAME/USER/PASSWORD/HOST/PORT`. `DJANGO_SECRET_KEY` is required unless `DEBUG=True` and `DJANGO_ALLOW_INSECURE_DEVELOPMENT=True`.
- WebSockets need ASGI/Daphne (`config.asgi:application`), not WSGI. Channel layer is in-memory unless `REDIS_URL` is set; Redis is only needed for multi-process/production.
- Custom admin: `config.admin.SocialConnectAdminConfig` → `config/admin_site.py`; overrides in `templates/admin/` and `static/admin/`.

## Verification (PowerShell, from `backend/`)
```powershell
..\venv\Scripts\python.exe manage.py check
..\venv\Scripts\python.exe manage.py makemigrations --check --dry-run
..\venv\Scripts\python.exe manage.py test --keepdb
..\venv\Scripts\python.exe manage.py test social --keepdb
..\venv\Scripts\python.exe manage.py test social.tests.SocialFeatureTests.test_feed_pagination_is_opt_in_and_returns_next_page --keepdb
```
- No pytest/tox config: use Django's test runner. Tests hit real Postgres; the DB user must be able to reuse/create the test DB. `--keepdb` avoids the interactive prompt that breaks non-interactive shells; the full suite is slow (~6 min).
- API tests are DRF `APITestCase` with `force_authenticate`; WebSocket tests are `TransactionTestCase` using Channels' `WebsocketCommunicator` against `config.asgi.application` (see `chat/tests.py`).

## Code wiring worth knowing
- `social/access.py` owns privacy/audience/block filtering (`visible_posts`, `can_view_profile`, ...). Reuse it, plus `with_post_serializer_prefetches()` when feeding `PostSerializer`; don't reimplement filters in views.
- Send notifications through `notifications.utils.create_notification`: it enforces block checks, `NotificationPreference` opt-outs, and on-commit WebSocket publishing.
- `users/apps.py:ready()` imports `users.signals` to auto-create `Profile`; register new signal receivers there.
- Chat deletes are soft (`Message.deleted_at`); every message query must exclude non-null `deleted_at`.
- JWT uses rotating/blacklisted refresh tokens; WebSocket clients pass `?token=<access>` through `chat.middleware.JWTAuthMiddleware`, not headers.
- Root reports (`runtime-validation-report.md`, `PROJECT_COMPLETION_REPORT.md`, etc.) are historical snapshots; verify with the commands above rather than trusting their claims.

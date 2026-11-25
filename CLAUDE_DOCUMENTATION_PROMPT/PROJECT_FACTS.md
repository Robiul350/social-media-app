# Project Facts

Verified facts about the workspace, stack, entrypoints, configuration, and evidence rules. These facts were derived from the current source/configuration files, not from historical completion reports. Environment variable **names** are listed only; no values are reproduced.

## 1. Workspace identity

| Fact | Evidence |
| --- | --- |
| Workspace root is `C:\Django project\social media app`. | Workspace metadata; root `README.md`, `AGENTS.md`. |
| The product is referred to as both "Social Media App" and "SocialConnect". | API root response in `backend/config/urls.py`; `frontend/index.html`, route titles in `frontend/src/App.jsx`, navbar/admin branding. Final official name requires user confirmation; see `USER_CONFIRMATION_REQUIRED.md`. |
| The root directory and `backend/` are separate Git repositories, both with zero commits; all files are effectively untracked. | `AGENTS.md`, `backend/AGENTS.md`. There is no commit history or `git diff` baseline. |
| There is no root-level build or test runner. | `AGENTS.md`. Verification is split between `backend/` and `frontend/`. |

## 2. Directory and application structure

| Area | Verified contents / responsibility |
| --- | --- |
| `backend/config/` | Django project configuration, root URLs, ASGI application, custom admin site, admin metrics, and a small unused `views.py`. |
| `backend/users/` | Custom user model, profile, story and story interaction models, auth/profile APIs, signals, admin registrations, tests, migrations. |
| `backend/posts/` | Posts, images, polls, bookmarks, hashtags, reports, related APIs, admin registrations, tests, migrations. |
| `backend/social/` | Likes, comments, mentions, comment reactions, follows, blocks, friend requests, feed, centralized access helpers, tests, migrations. |
| `backend/chat/` | Direct and group conversation models, REST APIs, WebSocket consumer, middleware, routing, utilities, tests, migrations. |
| `backend/notifications/` | Notification and preference models, REST APIs, WebSocket consumer, creation utility, routing, tests, migrations. |
| `frontend/src/` | React/Vite SPA entrypoint, router, API client, profile store, pages, components, hooks, utilities, styles. |
| `frontend/public/` | Favicon, icon sprite, service worker, web app manifest. |
| `backend/templates/admin/`, `backend/static/admin/` | Custom admin dashboard templates and static assets. |
| `postman/` | Minimal Postman workspace globals; not a populated API collection. |

## 3. Backend technology and runtime

| Fact | Evidence |
| --- | --- |
| Backend is Django 6.1 with Django REST Framework 3.18.0, SimpleJWT 5.5.1, Channels 4.3.2, channels_redis 4.3.0, Daphne 4.2.3, django-cors-headers 4.9.0, psycopg2-binary 2.9.12, Pillow 12.3.0, python-dotenv 1.2.2, and redis 8.1.0. | `backend/requirements.txt` lines 10, 11, 16–20, 28, 29, 35, 36; `backend/AGENTS.md`. |
| `AUTH_USER_MODEL` is the custom `users.User`. | `backend/config/settings.py`, user models. |
| PostgreSQL is mandatory; no SQLite fallback is configured. | `backend/config/settings.py`, `AGENTS.md`. |
| Root `.env` is the only environment file loaded by settings (`BASE_DIR.parent / ".env"`); `backend/.env` is not loaded. | `config/settings.py`, `AGENTS.md`. |
| The checkout already has a locally configured root `.env`; it must not be overwritten with `.env.example`. | `AGENTS.md`, root `README.md`. |
| `DJANGO_SECRET_KEY` is required in production; an insecure fallback exists only for explicitly enabled local development. | `config/settings.py`, root `README.md`, `AGENTS.md`. |
| WebSocket service requires ASGI (`config.asgi:application`), conventionally started with Daphne, not WSGI. | `config/asgi.py`, root `README.md`, `AGENTS.md`. |
| Channel layer uses Redis when `REDIS_URL` is set; otherwise an in-memory layer is used. Redis is only required for multi-process/production fan-out. | `config/settings.py`, `AGENTS.md`. |
| Default DRF authentication is JWT; access tokens are bearer tokens for HTTP and query-string tokens for WebSockets. | `config/settings.py`, `config/asgi.py`, `chat/middleware.py`, `frontend/src/api/axios.js`. |
| SimpleJWT uses rotating and blacklisted refresh tokens. | `config/settings.py`, auth views, `users` tests. |
| Install backend dependencies from `backend/requirements.txt`; root `requirements.txt` is an older/partial duplicate. | `AGENTS.md`, `backend/AGENTS.md`. |
| `config/settings.py` still carries a Django 6.0.4-generated docstring while requirements pin Django 6.1; this is a documentation-only mismatch. | `backend/config/settings.py:4`, `backend/requirements.txt:17`. |

## 4. Backend API and WebSocket surface

| Fact | Evidence |
| --- | --- |
| API prefixes are `/api/users/`, `/api/posts/`, `/api/social/`, `/api/notifications/`, and `/api/chat/`. | `backend/config/urls.py`. |
| Root URL returns a JSON health response with message, project label, version, and status. | `backend/config/urls.py`. |
| No ViewSets or `@action` decorators exist; all REST endpoints use `APIView`, DRF `generics.*APIView`, or SimpleJWT views. | Backend source audit across all five apps. |
| A second `home()` view exists in `backend/config/views.py` but is not routed. | `backend/config/views.py`, `config/urls.py`. |
| WebSocket routes are `ws/chat/<int:user_id>/` and `ws/notifications/`. | `config/asgi.py`, `chat/routing.py`, `notifications/routing.py`. |
| WebSocket access tokens are passed as `?token=<access_token>`. | `config/asgi.py`, `chat/middleware.py`, root `README.md`. |
| Custom admin is `config.admin.SocialConnectAdminConfig` → `config.admin_site.SocialConnectAdminSite`, with template/static overrides. | `backend/config/admin.py`, `admin_site.py`, `backend/templates/admin/`, `backend/static/admin/`. |
| Admin uses Django per-model permissions, Django groups for roles, and `LogEntry` for real activity history. | `config/admin_site.py`, `admin_metrics.py`, root `README.md`. |

## 5. Frontend technology and runtime

| Fact | Evidence |
| --- | --- |
| Frontend is React 19.3.1 + React DOM 19.3.1, React Router 7.18.5, Axios 1.21.0, built with Vite 8.3.6. | `frontend/package.json`. |
| Scripts are `dev`, `build`, `lint`, and `preview`; there is no `npm test` script and no frontend test files. | `frontend/package.json`; `AGENTS.md`. |
| Vitest and jsdom are installed as dev dependencies but unused by a current test suite. | `frontend/package.json`, `AGENTS.md`. |
| Use `npm.cmd` on this Windows checkout; `npm` resolves to a blocked PowerShell script. | `AGENTS.md`. |
| Entrypoint is `frontend/src/main.jsx` → `App.jsx`; the active stylesheet is `frontend/src/index.css`. `frontend/src/App.css` exists but is not imported. | `frontend/src/main.jsx`, `App.jsx`, source grep. |
| Service worker is registered only in production and precaches the app shell (`/`, `/index.html`) under cache `socialconnect-shell-v1`; navigation requests use a network-first fallback to `/index.html`. | `frontend/src/main.jsx`, `frontend/public/sw.js`. |
| Default API base URL is `http://127.0.0.1:8000/api/`; override with `VITE_API_BASE_URL`. `VITE_API_ORIGIN` controls media/WebSocket origins. | `frontend/src/api/axios.js`, root `README.md`. |
| Session state uses `localStorage` keys `access`, `refresh`, `user_id`, and `username`; theme uses `socialconnect-theme`. | `frontend/src/api/axios.js`, `navbar.jsx`, login/navbar/pages. |
| Cross-component events are `socialconnect:auth-change`, `socialconnect:profile-change`, and `socialconnect:refresh-counts`. | `api/axios.js`, `Login.jsx`, `EditProfile.jsx`, `AppShell.jsx`, `navbar.jsx`, `Messages.jsx`, `Notifications.jsx`. |
| Route guards check only the presence of `access`; a 401 refresh interceptor refreshes once, replays the request, and clears session on failure. | `frontend/src/App.jsx`, `frontend/src/api/axios.js`. |
| Profile data is cached by a small external store in `frontend/src/api/profileStore.js` with subscription and in-flight de-duplication. | `profileStore.js`. |
| The SPA has no `/explore` or `/settings` route; people discovery is `/search`, privacy controls are in Edit profile, and admin is Django `/admin/`. | `frontend/src/App.jsx`, root `README.md`, `AppShell.jsx`. |

## 6. Verification commands

From `backend/`:

```powershell
..\venv\Scripts\python.exe manage.py check
..\venv\Scripts\python.exe manage.py makemigrations --check --dry-run
..\venv\Scripts\python.exe manage.py test --keepdb
..\venv\Scripts\python.exe manage.py test social --keepdb
..\venv\Scripts\python.exe manage.py test social.tests.SocialFeatureTests.test_feed_pagination_is_opt_in_and_returns_next_page --keepdb
```

From `frontend/`:

```powershell
npm.cmd run lint
npm.cmd run build
```

Notes:

- `manage.py makemigrations --check --dry-run` was executed during this audit and returned `No changes detected`; there is no current model/migration drift.
- The test suite contains 9 test classes and 65 test methods across five files. Test discovery structure is verified; current pass/fail output is `[NOT VERIFIED - USER CONFIRMATION REQUIRED]` unless the suite is run.
- Backend tests use real PostgreSQL; `--keepdb` avoids an interactive database-creation prompt.
- WebSocket tests are `TransactionTestCase`s using Channels' `WebsocketCommunicator` against `config.asgi.application`, not Django test-client requests.
- No current pass/fail result is asserted here. Record actual output only if the command is executed.

## 7. Evidence hierarchy for Claude

Use this order when resolving a factual question:

1. Runtime source code (`models.py`, `views.py`, `serializers.py`, `urls.py`, `access.py`, `utils.py`, consumers, middleware, routing).
2. Migrations and tests.
3. Templates and static assets for admin/UI behavior.
4. Frontend source for reachable screens and interactions.
5. Companion evidence files in `CLAUDE_DOCUMENTATION_PROMPT/`.
6. Root `README.md` and `AGENTS.md` for setup/topology guidance.
7. Historical reports and `PROJECT_ANALYSIS/` only as claims requiring confirmation.

When evidence conflicts, cite both sources and use `[NOT VERIFIED - USER CONFIRMATION REQUIRED]`.

## 8. Security and privacy handling in documentation

- Never include secret values, tokens, credentials, or `.env` contents.
- Describe environment variables by name and purpose only.
- Privacy enforcement is centralized in `backend/social/access.py`; document it as application-layer filtering, not database row-level security.
- Notification creation is centralized in `backend/notifications/utils.py` with block checks, preference opt-outs, and on-commit WebSocket publishing.
- Chat deletes are soft (`Message.deleted_at`); every verified chat read path excludes deleted messages.

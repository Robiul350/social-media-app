# Runtime Validation Report

**Last updated:** 2026-11-24 full-stack synchronization/security pass: story upload fix, auth/token revocation, chat/notifications/post integration fixes, full backend suite, frontend lint/build, and backend checks. Browser smoke results below are from earlier validation passes.  
**Target:** `C:\Django project\social media app`

## Summary

| Step | Status | Exit Code | Details |
|---|---|---:|---|
| Vite startup | PASS | n/a | `npm.cmd run dev -- --host 127.0.0.1`; Vite ready at `http://127.0.0.1:5173/`. |
| Daphne startup | PASS | n/a | `daphne -b 127.0.0.1 -p 8001 config.asgi:application`; listening; `/` returned 200 and the protected unread-count route returned 401 without a token. |
| Backend integration | PASS | 0 | Latest full suite: 52 passed, 0 failed, 0 skipped (294.577 seconds); `--keepdb` preserved the existing test database. |
| Django system/migration checks | PASS | 0 | Latest `check` and `makemigrations --check --dry-run`; no pending model changes after aligning the existing `AdminAction` model state. |
| Frontend lint | PASS | 0 | Latest `npm.cmd run lint`. |
| Frontend production build | PASS | 0 | Latest `npm.cmd run build`: 105 modules; CSS 118.99 kB (gzip 22.28 kB), JS 449.62 kB (gzip 134.56 kB). |
| Admin JavaScript syntax | PASS | 0 | `node --check static\admin\js\socialconnect-dashboard.js`. |
| Browser validation | PARTIAL | n/a | Earlier integrated Playwright smoke flows passed; the latest premium SPA pages, Login/Register redesign, Stories, partial design restoration, and expanded admin UI were not browser-tested. |

`*` Browser tool calls returned successfully; this is not a Playwright CLI test-runner exit code.

## Partial Design Restoration (this pass)

Git had no commits and no project backups existed, so recovery used VS Code Local History. Only four snapshots were applied safely:

- `frontend/src/index.css` — original 2026-11-22 stylesheet appended last so original rules win where selectors overlap; current-only rules for newer components remain earlier in the cascade.
- `frontend/index.html` — original snapshot restored, removing the theme bootstrap script.
- `frontend/src/pages/Login.jsx` and `frontend/src/pages/Register.jsx` — original auth snapshots restored; a small functional guard was kept for password length/friendly API errors and the post-registration notice.

Snapshots for `App.jsx`, `home.jsx`, `navbar.jsx`, `UserProfile.jsx`, `UserSearch.jsx`, `PostActions.jsx`, and others were **not** applied because they predate required routes/features or would duplicate the AppShell sidebars. No backend, database, API, route, auth, chat, notification, media, or admin files were changed. No browser verification was performed for this restoration.

## Environment and Test Strategy

- **Docker:** UNAVAILABLE — Docker CLI was present, but `docker info` reported that the daemon was not responding.
- **Node.js:** AVAILABLE — v24.19.0.
- **Browser:** AVAILABLE — system Chrome and Edge were present; integrated browser/Playwright tools were used. The project does not have a local Playwright npm package or a configured browser-test suite.
- **Database:** PostgreSQL — the earlier audit suite used a unique temporary test database; the latest full suite used `--keepdb` and preserved the existing test database.
- **Channel layer:** In-memory — local `REDIS_URL` is unset. Redis-backed, multi-worker behavior was not verified.
- **Frontend/backend contract:** Django integration tests exercise the real API and PostgreSQL. Browser-authenticated flows against multiple accounts were not run.

## Backend Test Command

Earlier audit run (30 tests), executed from `backend` using a unique temporary test database:

```powershell
python -c "import os, uuid; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings'); import django; django.setup(); from django.conf import settings; settings.DATABASES['default'].setdefault('TEST', {})['NAME'] = 'sc_verify_test_' + uuid.uuid4().hex[:12]; from django.core.management import call_command; call_command('test', verbosity=2)"
```

The earlier audit run used a unique temporary PostgreSQL database after the ordinary test-database prompt conflicted with the non-interactive shell. For the latest run, the suite was executed from `backend` with `--keepdb` against the existing test database, which was preserved.

Latest command (run from `backend`):

```powershell
..\venv\Scripts\python.exe manage.py test --keepdb --verbosity 1
```

Result: 52 tests passed, 0 failed, 0 skipped; exit code 0; 294.577 seconds. The earlier 323.592-second 52-test result remains historical.

## Earlier Browser Smoke Flows

These were executed before the latest Login/Register redesign, Stories UI, premium SPA pass, partial design restoration, and story-privacy fix; they do not validate those latest changes.
1. Login page rendered with accessible username/password fields.
2. Registration route opened from login; submitting the empty form focused the required username field.
3. Registration password visibility toggle changed to the hide state.
4. Theme toggle changed modes.
5. Accessing `/connections/friends` without a session redirected to login.
6. At a 390 px viewport, the login page had no horizontal overflow (`document.documentElement.scrollWidth` was 303 px).
7. An intentionally invalid login returned the expected `Invalid username or password.` UI message for HTTP 400.

No successful authenticated browser login, profile upload, friend-request browser flow, or two-account real-time chat flow is claimed as tested.

## Test Evidence

- Latest Django full suite: 52 tests passed, 0 failed, 0 skipped, exit code 0, 294.577 seconds.
- Latest `manage.py check`: exit code 0.
- Latest `makemigrations --check --dry-run`: exit code 0; no pending model changes.
- Latest frontend ESLint: exit code 0.
- Latest Vite production build: exit code 0; 105 modules, CSS 118.99 kB (gzip 22.28 kB), JS 449.62 kB (gzip 134.56 kB).
- Partial design-restoration static check: CSS braces balanced (1,903 open / 1,903 close); only `src/index.css`, `src/pages/Login.jsx`, `src/pages/Register.jsx`, and `index.html` changed from the pre-restoration tree.
- Latest admin JavaScript syntax check: `node --check static\admin\js\socialconnect-dashboard.js`; exit code 0.
- Latest focused story-privacy API regression test: 1 passed; verified audience visibility, expiration, private-profile visibility, blocking, and inaccessible story-view responses.
- Focused `users.tests.SocialConnectAdminTests`: 9 passed; covers real KPI values, `Pending Reports`, previous-30-day trends, topbar collapse control, confirmation modal, all requested nav areas including `Settings`, cumulative/monthly/donut analytics keys, permission gating, roles/system views, and admin-scoped notification counts.
- No browser validation was performed for the expanded admin UI; layout and interaction claims are limited to implemented markup/CSS/JS and Django test responses.
- Notification migration `0004_alter_notification_notification_type` is applied to the configured database.
- Updated Daphne app returned HTTP 200 on port 8001. An attempted bind on port 8000 failed with `WinError 10048` because that port was already occupied; the existing process was not stopped or modified.

## Issues and Remaining Gaps

| # | Severity | Description | Escalated To |
|---:|---|---|---|
| 1 | Medium | Authenticated browser flows and live two-account messaging remain unverified. | User sign-off / follow-up |
| 2 | Medium | Redis-backed channel-layer behavior was not tested because `REDIS_URL` is unset and Docker is unavailable. | Deployment configuration |
| 3 | Scope | Stories now have a real-data SPA UI and server-side audience/privacy rules, but story reactions/viewer management, advanced post workflows, group real-time chat, creator analytics, PWA/localization, and other partial features listed in `PROJECT_COMPLETION_REPORT.md` remain incomplete. | Follow-up implementation |
| 4 | Scope | The expanded admin UI has no browser verification; report status/reviewer fields, persisted audit events, and automatic role assignment remain intentionally unimplemented pending approval. | User sign-off / follow-up |

## Verdict

```text
environment:
  docker: UNAVAILABLE — docker info reported the daemon was not responding
  node: AVAILABLE — v24.19.0
  playwright: AVAILABLE — integrated browser tools; no project-local Playwright package
  infra-tier: PRIMARY(PostgreSQL) — real PostgreSQL was used for integration tests
  browser-tier: PRIMARY(Playwright browser tools) — interactive SPA smoke checks executed
startup: PASS — Vite and updated Daphne process started during the earlier validation pass; ASGI root returned HTTP 200
integration: PASS — exit_code: 0, passed: 52, failed: 0, skipped: 0, 294.577 seconds; latest Django suite used --keepdb
e2e: PARTIAL — earlier browser smoke flows passed; latest premium SPA pages, Login/Register, Stories, and authenticated journeys were not browser-tested
overall: NEEDS_SIGNOFF — latest automated checks pass; authenticated browser/Redis validation and the remaining feature backlog are outstanding
```

## Latest authoritative run — 2026-11-24

| Step | Status | Details |
|---|---|---|
| `..\venv\Scripts\python.exe manage.py check` (from `backend`) | PASS | System check identified no issues. |
| `..\venv\Scripts\python.exe manage.py makemigrations --check --dry-run` (from `backend`) | PASS | No changes detected. |
| `..\venv\Scripts\python.exe manage.py test --keepdb` (from `backend`) | PASS | 60 tests, 0 failures, 0 skipped, 347.100 seconds. PostgreSQL test DB preserved. |
| `npm.cmd run lint` (from `frontend`) | PASS | No ESLint output/errors. |
| `npm.cmd run build` (from `frontend`) | PASS | 105 modules; `index-BU3wgyY_.css` 123.80 kB (gzip 23.08 kB); `index-7sch0qJ1.js` 451.58 kB (gzip 135.16 kB). |
| Focused security tests | PASS | Password reset token exposure, refresh-token revocation after password change/deactivate/reset, chat attachment validation, group blocked-member filtering, draft author access, notification target hiding. |

No browser, Redis multi-worker, or production media-serving verification was run in this pass. The backend suite used the real configured PostgreSQL test database via `--keepdb`; no database reset or record deletion occurred.

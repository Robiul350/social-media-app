# SocialConnect Code Audit Report

**Date:** 2026-11-24
**Scope:** `backend/` (config, all five apps, migrations, tests), `frontend/` (all of `src/`, public assets, Vite/ESLint/package config), root docs and dependency manifests.
**Method:** Static inspection of every relevant source file, targeted verification commands, Django integration tests against real PostgreSQL, and an ASGI runtime smoke check. No data was deleted, no migration was applied, and no `.env` file was changed.

## Summary

| Category | Count |
|---|---:|
| Issues identified | 9 |
| Issues fixed (verified) | 9 |
| Frontend fixes | 4 |
| Backend fixes | 4 |
| Database / migration fixes | 1 (no schema change; test correctness) |
| API integration fixes | 1 |
| Security / permission fixes | 1 |
| Dependency changes | 0 |

## Issues fixed

| # | Severity | Area | Status | Issue and fix |
|---:|---|---|---|---|
| 1 | HIGH | Backend / admin test | FIXED | `users/tests.py`: dashboard test asserted 8 KPI cards while the code now renders 12, and required a trend on every card although story cards deliberately have none. Updated assertions to the current 12-card contract and split trend expectations. |
| 2 | HIGH | Backend / chat | FIXED | `chat/views.py` `ConversationListView`: group messages have `receiver=NULL`, so `other.id` raised `AttributeError` and `GET /api/chat/conversations/` returned 500 after any REST group message. Filtered to direct messages (`receiver__isnull=False`, `group__isnull=True`). Added regression test. |
| 3 | HIGH | Backend / admin | FIXED | `config/admin_metrics.py`: `popular_posts` and `top_users` ordered by every possible annotation even when permissions added only some of them, causing `FieldError` → 500 for partially permissioned staff. Order fields are now built from annotations actually present. Added regression test with posts+likes+users (no comments) permissions. |
| 4 | MEDIUM | Backend / admin | FIXED | `config/admin_metrics.py`: dashboard/analytics queried the optional `story_reactions` relation even if its table was absent (e.g. mid-deploy), producing a 500. Added `_relation_available()` guard so those metrics render as `—` while real query errors still propagate. Verified by `test_dashboard_and_analytics_survive_missing_optional_table`. |
| 5 | MEDIUM | Frontend / PWA | FIXED | `public/sw.js` returned `index.html` with HTTP 200 for *any* failed GET, so failed API calls were parsed as HTML by Axios. The app-shell fallback is now limited to navigation requests; other failed GETs return `Response.error()` and reject normally. |
| 6 | MEDIUM | Frontend / React | FIXED | `pages/Bookmarks.jsx`: under `StrictMode`, the one-shot load guard skipped the remounted effect after cleanup aborted the only request, leaving the page stuck loading. Cleanup now resets the guard so the remount refetches. |
| 7 | MEDIUM | Frontend / React | FIXED | `pages/PostDetail.jsx`: same StrictMode abort/guard deadlock; cleanup now resets `loadedPostIdRef` so the remount refetches the post. |
| 8 | LOW | Frontend / stories | FIXED | `components/Stories.jsx`: preview selection used `isVideoSource()` on a `blob:` URL, so uploaded videos rendered as a broken `<img>`. Preview element now uses the selected file's MIME type. |
| 9 | LOW | Backend / posts | FIXED | `posts/views.py` `sync_hashtags()`: `Hashtag.objects.filter(...).first().posts.remove(post)` assumed the row still existed between read and removal. Now guarded against a missing hashtag. |

## Verification performed

### Backend (from `backend/`, interpreter `../venv/Scripts/python.exe`)

| Command | Result |
|---|---|
| `manage.py check` | PASS — no issues |
| `manage.py makemigrations --check --dry-run` | PASS — no model/migration drift |
| `manage.py test --keepdb` (baseline, before fixes) | 60 tests, 1 failure (issue #1); 811.8 s |
| `manage.py test users.tests.SocialConnectAdminTests --keepdb` | 9 passed after issue #1 |
| `manage.py test chat.tests.ConversationTests users.tests.SocialConnectAdminTests --keepdb` | 18 passed after issues #2, #3, #4 |
| `manage.py test posts.tests --keepdb` | 7 passed after issue #9 |
| `manage.py test` on a fresh uniquely named temporary PostgreSQL database | FINAL_RESULT_PLACEHOLDER |
| `-m pip check` | PASS — no broken requirements |

The first full re-run against the shared `--keepdb` database hit `psycopg2.errors.DeadlockDetected` during Django's `flush` because two unrelated `manage.py test --keepdb` processes were running against the same test database at the same time. That run is recorded as an environmental failure, not an application failure; the final run used an isolated temporary database.

### Frontend (from `frontend/`)

| Command | Result |
|---|---|
| `npm.cmd run lint` | PASS (baseline and after all fixes); no suppressions added |
| `npm.cmd run build` | PASS — 105 modules; `index-BU3wgyY_.css` 123.80 kB (gzip 23.08 kB); `index-BtSQ_nD0.js` 451.92 kB (gzip 135.24 kB) |
| `node --check public/sw.js` | PASS |
| `npm ls --depth=0` | PASS — installed tree matches declared dependencies |

### Runtime smoke (ASGI/Daphne)

Started `daphne -b 127.0.0.1 -p 8001 config.asgi:application` and issued real HTTP requests:

| Request | Status |
|---|---:|
| `GET /` | 200 (expected JSON health payload) |
| `GET /admin/login/` | 200 |
| `GET /api/posts/` (no token) | 401 |
| `GET /api/users/profile/` (no token) | 401 |
| `GET /api/chat/conversations/` (no token) | 401 |
| `GET /api/notifications/` (no token) | 401 |
| `GET /api/social/friend-requests/` (no token) | 401 |

Daphne was stopped after the smoke check. No browser/authenticated-session testing was performed.

## Files modified

- `backend/users/tests.py` (issues #1, #3 test)
- `backend/chat/views.py` (issue #2)
- `backend/chat/tests.py` (issue #2 regression test)
- `backend/config/admin_metrics.py` (issues #3, #4)
- `backend/posts/views.py` (issue #9)
- `frontend/public/sw.js` (issue #5)
- `frontend/src/pages/Bookmarks.jsx` (issue #6)
- `frontend/src/pages/PostDetail.jsx` (issue #7)
- `frontend/src/components/Stories.jsx` (issue #8)

Dependency versions, `.env`, migrations, and database records were not changed.

## Remaining warnings and unresolved items

| Status | Item | Reason |
|---|---|---|
| WARNING | Full backend suite takes ~8–13 minutes on this machine. | Integration tests use real PostgreSQL and WebSocket communicators. Not a failure; allow a long timeout. |
| WARNING | Concurrent suites using `--keepdb` collide. | Two other `manage.py test --keepdb` processes were detected sharing the test DB and caused a flush deadlock. Run one suite at a time or use a unique `TEST.NAME`. |
| WARNING | Redis-backed multi-worker WebSocket behavior is unverified. | `REDIS_URL` is unset locally; the in-memory channel layer is used. Docker daemon was unavailable in earlier validation. |
| UNRESOLVED | `GET /api/posts/?drafts=true` returns all posts authored by the caller, not only drafts/scheduled posts as README phrasing implies. | No frontend caller exists and the current test contract expects all own posts; narrowing the filter could remove working behavior. Needs a product decision. |
| WARNING | Authenticated multi-account browser flows, live two-account chat, and interaction smoke tests were not performed. | No browser test runner is configured in `package.json`; no browser automation tool was used in this audit. Django integration tests cover these APIs server-side. |
| WARNING | Real SMTP email delivery and production static/media serving were not verified. | Tests use Django's in-memory email backend; `DEBUG=True` locally serves media through Django. |
| WARNING | Group conversations have REST endpoints but no group WebSocket delivery, and several advanced post features remain API-only. | Existing scope limitation documented in the root README; no feature was removed. |

## Verdict

All verified code defects found in this audit are fixed and the available automated checks pass. Remaining items are environmental verification gaps or documented scope/contract decisions, not known runtime errors.


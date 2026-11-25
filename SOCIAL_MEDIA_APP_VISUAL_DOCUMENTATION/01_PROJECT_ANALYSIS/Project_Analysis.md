# Project Analysis

## Scope and evidence rule

This analysis is derived from the current source tree only. Generated folders (`node_modules`, `venv`, `__pycache__`, `.git`, `build`, `dist`) were ignored. Historical reports and `PROJECT_ANALYSIS/` were treated as claims requiring confirmation, never as proof. The exact acceptance marker for unresolved information is `[NOT VERIFIED - USER CONFIRMATION REQUIRED]`.

No application source, configuration, media, or repository file was modified. Every generated asset is inside `SOCIAL_MEDIA_APP_VISUAL_DOCUMENTATION/`.

## Product identity

The API root reports `"project": "Social Media App"`. The React document title, route titles, inline auth UI, and custom Django admin use `SocialConnect`. Until the owner confirms the submission brand, all visual deliverables use `Social Media App (working UI/admin name: SocialConnect)`. The final official name is `[NOT VERIFIED - USER CONFIRMATION REQUIRED]`.

## Technology stack identified from source

| Layer | Verified technology |
| --- | --- |
| Frontend | React 19.3.1, React DOM 19.3.1, React Router 7.18.5, Axios 1.21.0, Vite 8.3.6 |
| Backend | Django 6.1, Django REST Framework 3.18.0, SimpleJWT 5.5.1, Channels 4.3.2, channels_redis 4.3.0, Daphne 4.2.3, django-cors-headers 4.9.0 |
| Database | PostgreSQL via psycopg2-binary 2.9.12; no SQLite fallback configured |
| Real time | ASGI `config.asgi:application`; Redis channel layer when `REDIS_URL` is set, otherwise in-memory |
| Admin | Custom `SocialConnectAdminSite` at `/admin/`, not a React route |
| Frontend tests | Vitest/jsdom/testing-library installed but no `npm test` script and no test files found |
| Backend tests | 9 test classes and 65 test methods across five files; current pass/fail output `[NOT VERIFIED - USER CONFIRMATION REQUIRED]` |
| PWA | Production-only service worker caching `/` and `/index.html`; no offline data or push |

## Application structure

| Area | Verified responsibility |
| --- | --- |
| `backend/config/` | Settings, root URLs, ASGI application, custom admin site, admin metrics |
| `backend/users/` | Custom user model, profile, stories, story interactions, auth/profile APIs, signals |
| `backend/posts/` | Posts, images, polls, bookmarks, hashtags, reports, related APIs |
| `backend/social/` | Likes, comments, mentions, comment reactions, follows, blocks, friend requests, feed, access helpers |
| `backend/chat/` | Direct and group conversation models, REST APIs, WebSocket consumer, middleware |
| `backend/notifications/` | Notification/preference models, REST APIs, WebSocket consumer, creation utility |
| `frontend/src/` | React entrypoint, router, API client, profile store, pages, components, hooks, styles |
| `backend/templates/admin/`, `backend/static/admin/` | Custom admin dashboard templates and static assets |

## Reachable SPA routes

`/login`, `/register`, `/` (home feed), `/search`, `/edit-profile`, `/messages`, `/messages/:userId`, `/notifications`, `/friend-requests`, `/connections/:section`, `/bookmarks`, `/profile` redirect, `/posts/:postId`, `/users/:userId`, plus a wildcard fallback to `/`.

There is no verified `/explore`, `/settings`, `/forgot-password`, `/password-reset-confirm`, `/groups`, `/polls`, or moderation SPA route. Mockups for those areas are explicitly labelled proposed.

## Backend API surface

Five prefixes are routed under `/api/`: `users/`, `posts/`, `social/`, `notifications/`, `chat/`. There are no ViewSets and no `@action` decorators. REST endpoints use `APIView`, DRF `generics.*APIView`, or SimpleJWT views. WebSocket routes are `ws/chat/<user_id>/?token=<access>` and `ws/notifications/?token=<access>`.

## Cross-cutting behavior

- HTTP authentication uses `Authorization: Bearer <access>`; WebSocket authentication uses a query-string token.
- SimpleJWT refresh tokens rotate and are blacklisted.
- The SPA stores `access`, `refresh`, `user_id`, and `username` in `localStorage`; route guards check token presence only.
- Axios refreshes once on 401, replays the request, shares concurrent refreshes, and clears the session on failure.
- Privacy and audience filtering are centralized in `backend/social/access.py` as application-layer query filtering, not database row-level security.
- Notification creation is centralized in `backend/notifications/utils.py` with self/block checks, preference opt-outs, persistence, and `transaction.on_commit` channel publishing.
- Chat deletes are soft through `Message.deleted_at`; verified read paths exclude deleted rows.
- Production deployment topology, static/media hosting, Redis deployment, email delivery, and monitoring are `[NOT VERIFIED - USER CONFIRMATION REQUIRED]`.

## Verification commands from source guidance

From `backend/`:

```powershell
..\venv\Scripts\python.exe manage.py check
..\venv\Scripts\python.exe manage.py makemigrations --check --dry-run
..\venv\Scripts\python.exe manage.py test --keepdb
```

From `frontend/`:

```powershell
npm.cmd run lint
npm.cmd run build
```

`manage.py makemigrations --check --dry-run` was executed during the source audit and returned `No changes detected`. Current results for the other commands are `[NOT VERIFIED - USER CONFIRMATION REQUIRED]` unless they are actually run and recorded.

## Status vocabulary

| Status | Meaning |
| --- | --- |
| Implemented | Backend logic and a reachable UI/API path are present with no known blocking gap in the primary flow. |
| Partial | Code exists, but part of the end-to-end flow, UI, notification, ordering, validation, or lifecycle is incomplete. |
| Backend only | REST/WebSocket/model capability exists in Django; no corresponding SPA screen or action was found. |
| Planned / documented | Mentioned in historical docs or field intent but not proven in active source. |
| Not Found | No supporting route, model, endpoint, component, test, or job was found. |
| Needs Verification | Runtime, environment, deployment, or owner confirmation is required. |

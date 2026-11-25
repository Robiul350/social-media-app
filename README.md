# SocialConnect

SocialConnect is a Django REST Framework, Django Channels, and React social media application.

## Requirements

- Python 3.13
- Node.js 20+
- PostgreSQL
- Redis (optional locally; Django Channels uses an in-memory layer when `REDIS_URL` is unset)

## Backend setup

```powershell
cd "C:\Django project\social media app"
# Fresh clones only: copy .env.example .env. In this checkout .env already exists and is locally configured; do not overwrite it.
.\venv\Scripts\python.exe -m pip install -r backend\requirements.txt
cd backend
..\venv\Scripts\python.exe manage.py migrate
..\venv\Scripts\python.exe manage.py runserver
```

Configure PostgreSQL credentials in `.env`. WebSocket support can be started with:

```powershell
cd backend
..\venv\Scripts\daphne.exe -p 8000 config.asgi:application
```

Set `REDIS_URL=redis://127.0.0.1:6379` to use Redis across multiple server processes.
For local development with Docker installed, start Redis with:

```powershell
docker run --name socialconnect-redis --restart unless-stopped -p 6379:6379 -d redis:7-alpine
```

The in-memory channel layer is suitable only for a single local development process;
use Redis for multi-worker or production deployments. Start the ASGI server with
Daphne (not Django's WSGI server) to accept WebSocket connections.

### Production HTTPS settings

The local `.env.example` is configured for HTTP development. For an HTTPS-only
production deployment, set `DJANGO_DEBUG=False` and configure a private,
high-entropy `DJANGO_SECRET_KEY` in the untracked `.env` or deployment secret store.
Generate a key with:

```powershell
..\venv\Scripts\python.exe -c "import secrets; print(secrets.token_urlsafe(64))"
```

With debug disabled, HTTPS redirects, secure session/CSRF cookies, and a one-year
HSTS policy are enabled by default. HSTS for subdomains and browser preload are
intentionally opt-in: enable them only after confirming every subdomain uses HTTPS
and you intend the long-lived browser policy. If TLS terminates at a trusted reverse
proxy, set `DJANGO_USE_HTTPS_PROXY=True` only when that proxy overwrites
`X-Forwarded-Proto` with the actual protocol. Configure `DJANGO_ALLOWED_HOSTS` and
`CORS_ALLOWED_ORIGINS` with the production hostnames/origins. Django refuses to
start in production mode without `DJANGO_SECRET_KEY`.

## Frontend setup

```powershell
cd "C:\Django project\social media app\frontend"
npm install
npm run dev
```

The frontend opens through Vite, normally at `http://localhost:5173`.

The React app provides protected feed/profile/search/chat/notification pages, a
paginated public feed, post media previews, nested comments, likes, bookmarks,
reporting, suggested accounts, responsive navigation, and a persistent light/dark
theme. Stories and group conversations have backend APIs but are not yet integrated
into the active frontend. API requests use the real Django endpoints listed below.
By default, the frontend connects to `http://127.0.0.1:8000/api/`; override
`VITE_API_BASE_URL` in a `frontend/.env` file when the API is hosted elsewhere.
`VITE_API_ORIGIN` may be set when media or WebSocket traffic uses a different origin.
The current app has no standalone `/explore` or `/settings` route: `/search` is
people discovery, profile privacy controls live in Edit profile, the theme toggle
is in the top navigation, and notification preferences are exposed by the API.
The Admin Dashboard is the Django admin at `/admin/`.

Production build:

```powershell
npm.cmd run build
```

## Django administration

Open `http://127.0.0.1:8000/admin/` and sign in with an existing staff/superuser account.
Create a new local superuser with:

```powershell
cd "C:\Django project\social media app\backend"
..\venv\Scripts\python.exe manage.py createsuperuser
```

The admin overview uses live database counts and six-month activity charts. The expanded
admin also includes a permission-gated Analytics page, real admin activity history, Django
group-based roles, and verifiable system status. Admin access continues to use Django's
per-model permissions; messages, groups, preferences, and admin logs are view-only. Profile
and post media previews require the configured media storage to be reachable by the admin browser.
Set `FRONTEND_URL` in `.env` to the frontend origin used by the admin's “Back to website” link.
Run `..\venv\Scripts\python.exe manage.py collectstatic` when deploying static assets.

## Main API routes

- `POST /api/users/register/`
- `POST /api/users/login/`
- `POST /api/users/logout/`
- `POST /api/users/token/refresh/`
- `GET/PATCH /api/users/profile/`
  - Multipart `PATCH` accepts `profile_picture` and `cover_photo` uploads.
  - Send `remove_profile_picture=true` or `remove_cover_photo=true` to remove the current image.
- `GET /api/users/search/?search=...`
- `GET /api/users/search/?suggested=true` (up to five accounts not followed by the current user)
- `GET /api/users/<id>/`
- `GET /api/users/<id>/posts/`
- `GET/POST /api/users/stories/`
- `POST /api/users/stories/<id>/view/`
- `GET/POST /api/posts/`
- `GET /api/posts/?bookmarked=true`
- `GET/PATCH/DELETE /api/posts/<id>/`
- `POST /api/posts/<id>/bookmark/`
- `POST /api/posts/<id>/pin/`
- `POST /api/posts/<id>/repost/`
- `POST /api/posts/<id>/report/`
- `POST /api/posts/<id>/poll/<option_id>/vote/`
- `POST/DELETE /api/social/users/<id>/follow/`
- `POST /api/social/users/<id>/friend-request/`
- `GET /api/social/friend-requests/?direction=incoming|outgoing`
- `POST /api/social/friend-requests/<id>/accept/`
- `POST /api/social/friend-requests/<id>/reject/`
- `DELETE /api/social/friend-requests/<id>/` (sender cancels a pending request)
- `GET /api/social/friends/`
- `DELETE /api/social/friends/<id>/` (unfriend)
- `GET /api/social/users/followers/`
- `GET /api/social/users/following/`
- `GET /api/social/users/<id>/mutual-friends/`
- `POST /api/social/posts/<id>/like/`
- `GET/POST /api/social/posts/<id>/comments/` (`POST` accepts an optional `parent` comment ID for replies)
- `POST /api/social/comments/<id>/react/`
- New top-level comments notify the post author; replies notify the parent comment author.
- `GET/PATCH/DELETE /api/social/comments/<id>/`
- `GET /api/social/feed/`
- `GET /api/social/feed/?page=1` (optional 10-post pages; the unpaged response remains available)
- `GET/POST /api/chat/conversations/<user_id>/`
- `GET /api/chat/conversations/`
- `POST /api/chat/conversations/<user_id>/read/`
- `GET /api/chat/unread-count/`
- `GET/POST /api/chat/groups/`
- `GET/POST /api/chat/groups/<group_id>/messages/`
- `PATCH/DELETE /api/chat/messages/<id>/`
- `GET /api/notifications/`
- `POST /api/notifications/read-all/`
- `PATCH /api/notifications/<id>/read/`
- `GET/PATCH /api/notifications/preferences/`
- WebSocket: `ws://127.0.0.1:8000/ws/chat/<user_id>/?token=<access_token>`
  - JSON `{"message":"..."}` sends a message; typing and presence events are broadcast to both participants.
  - Opening a conversation marks incoming messages as read and broadcasts read receipts.
- WebSocket: `ws://127.0.0.1:8000/ws/notifications/?token=<access_token>`
  - Sends new notification events to the authenticated recipient; the SPA reconnects and refreshes access tokens after a disconnect.

The connections page uses the existing friends, followers, and following APIs.
The feed supports bookmarks, public/unfollowed posts, privacy and block filtering,
and up to five unfollowed account suggestions. Stories and group messaging have
backend models/routes; story list and view endpoints enforce story audience,
expiration, private-profile visibility, and blocks, but the active frontend does
not yet provide a complete Stories experience. Group messages are not delivered
over a group WebSocket. Post models
include polls, audience controls, drafts, scheduling, pinning, reposts, reports,
hashtags, and additional image records, but several of these remain API-only or
partially wired and are not represented as fully supported frontend features.
The Login page now uses the shared design tokens; this does not imply a complete
redesign of every application page. The current backend suite contains 52 passing
tests; the latest admin changes were validated by automated checks but not browser-tested.

## Validation

```powershell
cd backend
..\venv\Scripts\python.exe manage.py check
..\venv\Scripts\python.exe manage.py makemigrations --check --dry-run
..\venv\Scripts\python.exe manage.py test --keepdb

cd ..\frontend
npm.cmd run lint
npm.cmd run build
```

## Current integration notes (2026-11-24)

- `DJANGO_SECRET_KEY` must be present in the root `.env`. The built-in insecure fallback is used only when `DJANGO_DEBUG` is enabled **and** `DJANGO_ALLOW_INSECURE_DEVELOPMENT=True` is set explicitly.
- Password reset requests always return the same generic response. When an active account matches the email, a reset link is emailed using Django's configured email backend; the token is never returned in the API response.
- Password change, password reset confirmation, and account deactivation blacklist all outstanding JWT refresh tokens for that user.
- Chat attachments are supported by `POST /api/chat/conversations/<user_id>/` via multipart form data. Maximum size is 25 MB; allowed types are images, video, audio, PDF, and plain text.
- Authors can list their own drafts/scheduled posts with `GET /api/posts/?drafts=true` and can retrieve/edit a draft by ID. Other users cannot see them.
- `npm.cmd` is required on this Windows checkout because `npm` resolves to a blocked PowerShell script.
# social-media-app

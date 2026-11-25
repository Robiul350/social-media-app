# Project Structure

## Root layout

```text
C:\Django project\social media app\
├── backend/                         Django 6.1 REST/Channels API and custom admin
├── frontend/                        Vite + React SPA
├── PROJECT_ANALYSIS/                This audit (created for documentation only)
├── .env                             Local environment file (never inspected/reproduced)
├── .env.example                     Environment variable template (names only documented)
├── .gitignore                       Root ignore rules
├── .postman/                        Postman workspace resources
├── .vscode/                         Editor settings
├── AGENTS.md                        Workspace notes and verification commands
├── API_INTEGRATION_REPORT.md         Historical integration snapshot
├── BUG_FIX_REPORT.md                 Historical bug-fix snapshot
├── CODE_AUDIT_REPORT.md              Historical code-audit snapshot
├── IMPLEMENTATION_REPORT.md          Historical implementation snapshot
├── PROJECT_COMPLETION_REPORT.md      Historical completion snapshot
├── README.md                        Existing project README
├── requirements.txt                  Older/partial dependency duplicate
└── runtime-validation-report.md      Historical validation snapshot
```

Dependency/cache folders were pruned from the discovery tree: `node_modules`, `venv`, `.git`, `__pycache__`, `dist`, `.pytest_cache`.

## Source-focused tree

```text
.
├── backend/
│   ├── config/
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── admin_metrics.py
│   │   ├── admin_site.py
│   │   ├── asgi.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── views.py
│   │   ├── wsgi.py
│   │   └── output/dd.exe                 Unusual committed binary artifact
│   ├── chat/
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── consumers.py
│   │   ├── middleware.py
│   │   ├── models.py
│   │   ├── routing.py
│   │   ├── serializers.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   ├── utils.py
│   │   ├── views.py
│   │   └── migrations/ (0001-0002)
│   ├── notifications/
│   │   ├── admin.py, apps.py, consumers.py, models.py, routing.py,
│   │   ├── serializers.py, tests.py, urls.py, utils.py, views.py
│   │   └── migrations/ (0001-0006)
│   ├── posts/
│   │   ├── admin.py, apps.py, models.py, permissions.py, serializers.py,
│   │   ├── tests.py, urls.py, views.py
│   │   └── migrations/ (0001-0002)
│   ├── social/
│   │   ├── access.py, admin.py, apps.py, models.py, permissions.py,
│   │   ├── serializers.py, tests.py, urls.py, views.py
│   │   └── migrations/ (0001-0005)
│   ├── users/
│   │   ├── admin.py, admin_action.py, apps.py, models.py, serializers.py,
│   │   ├── signals.py, tests.py, urls.py, views.py
│   │   └── migrations/ (0001-0007)
│   ├── manage.py
│   ├── requirements.txt               Authoritative backend dependencies
│   ├── media/                          Local uploaded content (not reproduced)
│   ├── static/admin/                   Custom admin CSS/JS
│   └── templates/admin/                Custom admin HTML overrides
├── frontend/
│   ├── public/
│   │   ├── favicon.svg
│   │   ├── icons.svg
│   │   ├── manifest.webmanifest
│   │   └── sw.js
│   ├── src/
│   │   ├── api/axios.js, profileStore.js
│   │   ├── components/
│   │   │   ├── AppShell.jsx
│   │   │   ├── AuthWelcomePanel.jsx
│   │   │   ├── ConfirmDialog.jsx
│   │   │   ├── CreatePost.jsx
│   │   │   ├── Icon.jsx
│   │   │   ├── MediaViewer.jsx
│   │   │   ├── PostActions.jsx
│   │   │   ├── Stories.jsx
│   │   │   ├── UserAvatar.jsx
│   │   │   ├── navbar.jsx
│   │   │   └── NotificationSettingsDialog.jsx
│   │   ├── hooks/useFocusTrap.js
│   │   ├── pages/
│   │   │   ├── Bookmarks.jsx
│   │   │   ├── Connections.jsx
│   │   │   ├── EditProfile.jsx
│   │   │   ├── FriendRequests.jsx
│   │   │   ├── home.jsx
│   │   │   ├── Login.jsx
│   │   │   ├── Messages.jsx
│   │   │   ├── Notifications.jsx
│   │   │   ├── PostDetail.jsx
│   │   │   ├── Profile.jsx                 Exists but is not imported by App.jsx
│   │   │   ├── Register.jsx
│   │   │   ├── UserProfile.jsx
│   │   │   └── UserSearch.jsx
│   │   ├── utils/formErrors.js
│   │   ├── App.css
│   │   ├── App.jsx
│   │   ├── index.css
│   │   └── main.jsx
│   ├── .gitignore
│   ├── eslint.config.js
│   ├── index.html
│   ├── package.json
│   ├── package-lock.json
│   ├── README.md
│   └── vite.config.js
├── postman/globals/workspace.globals.yaml
└── .postman/resources.yaml
```

## Directory responsibilities

### `backend/config/`

Project-level Django configuration. `settings.py` loads the root `.env`, configures installed apps, middleware, DRF/JWT, CORS, PostgreSQL, channel layers, media/static paths, and the custom admin. `urls.py` mounts API roots and DEBUG media serving. `asgi.py` combines HTTP and WebSocket routing. `admin_site.py` and `admin_metrics.py` implement the custom admin dashboard. `views.py` contains a separate/simple JSON home response, while `urls.py` defines its own `home` function directly.

### `backend/users/`

Custom user/profiles, registration and login, logout with blacklisting, password change/reset, deactivation, user search, public profiles, user posts, stories, story views, and story reactions. `apps.py` imports `signals.py` to auto-create `Profile`. `admin_action.py` is present but the `AdminAction` model is not used as an audit source in source comments.

### `backend/posts/`

Content model and serialization: posts, images, audience/drafts/pinning/scheduling/reposts, bookmarks, polls, poll options/votes, hashtags, and reports. `permissions.py` protects author-only edit/delete operations.

### `backend/social/`

Social interactions and feed privacy. `access.py` centralizes visibility, audience, and block checks. Models cover likes, comments with parent replies, mentions, comment reactions, follows, friend requests, and blocks. Views expose feed, like/comment, friend/follow/block endpoints.

### `backend/notifications/`

Notification model/preferences/serializers/API, utilities for creating notifications with block/preference checks and WebSocket publishing, and a notification consumer/routing module.

### `backend/chat/`

Direct-message and group-conversation models, serializers, REST views/routes, a direct WebSocket consumer, JWT query-token middleware, group naming utility, and admin registrations. Chat deletes are soft (`deleted_at`).

### `frontend/src/`

Router and protected layout (`App.jsx`), Axios API layer with JWT refresh (`api/axios.js`), profile cache (`api/profileStore.js`), shell/navigation, shared dialogs/media components, page screens, hooks, utilities, and a large centralized stylesheet (`index.css`).

## Size snapshot

Measured with line counts over source files, excluding dependencies and generated caches:

| Area | Lines |
| --- | ---: |
| Backend Python (excluding migrations) | ~7,936 |
| Frontend JS/JSX | ~7,361 |
| Frontend CSS | ~13,812 |
| Backend tests | ~2,025 |
| Main frontend page files | ~5,400 JSX lines |

The very large frontend stylesheet contains repeated theme/responsive blocks; this is noted as a maintainability issue in `BUGS_AND_RECOMMENDATIONS.md`.

## Not Found in structure

- No root-level build/test runner script.
- No frontend test files or `npm test` script.
- No OpenAPI/Schema/Swagger route in the URL configuration.
- No dedicated deployment directory (Docker, nginx, systemd, CI/CD) in the pruned source tree.
- No production static serving module for the SPA build output.

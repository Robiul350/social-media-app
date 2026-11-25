"""Generate Phase 1 analysis, data dictionary, requirements, and spreadsheet deliverables."""

from __future__ import annotations

import html
import zipfile
from pathlib import Path

from vizlib import write_text

ROOT = Path(__file__).resolve().parents[1]
A01 = ROOT / "01_PROJECT_ANALYSIS"
A04 = ROOT / "04_ER_DIAGRAM"
A08 = ROOT / "08_USER_REQUIREMENTS"
A09 = ROOT / "09_TRACEABILITY"
A10 = ROOT / "10_TESTING"

VOCAB = [
    ("Implemented", "Backend logic and a reachable UI/API path are present with no known blocking gap in the primary flow."),
    ("Partial", "Code exists, but part of the end-to-end flow, UI, notification, ordering, validation, or lifecycle is incomplete."),
    ("Backend only", "REST/WebSocket/model capability exists in Django; no corresponding SPA screen or action was found."),
    ("Planned / documented", "Mentioned in historical docs or field intent but not proven in active source."),
    ("Not Found", "No supporting route, model, endpoint, component, test, or job was found."),
    ("Needs Verification", "Runtime, environment, deployment, or owner confirmation is required."),
]

UNVERIFIED = "[NOT VERIFIED - USER CONFIRMATION REQUIRED]"

ANALYSIS = """# Project Analysis

## Scope and evidence rule

This analysis is derived from the current source tree only. Generated folders (`node_modules`, `venv`, `__pycache__`, `.git`, `build`, `dist`) were ignored. Historical reports and `PROJECT_ANALYSIS/` were treated as claims requiring confirmation, never as proof. The exact acceptance marker for unresolved information is `{u}`.

No application source, configuration, media, or repository file was modified. Every generated asset is inside `SOCIAL_MEDIA_APP_VISUAL_DOCUMENTATION/`.

## Product identity

The API root reports `"project": "Social Media App"`. The React document title, route titles, inline auth UI, and custom Django admin use `SocialConnect`. Until the owner confirms the submission brand, all visual deliverables use `Social Media App (working UI/admin name: SocialConnect)`. The final official name is `{u}`.

## Technology stack identified from source

| Layer | Verified technology |
| --- | --- |
| Frontend | React 19.3.1, React DOM 19.3.1, React Router 7.18.5, Axios 1.21.0, Vite 8.3.6 |
| Backend | Django 6.1, Django REST Framework 3.18.0, SimpleJWT 5.5.1, Channels 4.3.2, channels_redis 4.3.0, Daphne 4.2.3, django-cors-headers 4.9.0 |
| Database | PostgreSQL via psycopg2-binary 2.9.12; no SQLite fallback configured |
| Real time | ASGI `config.asgi:application`; Redis channel layer when `REDIS_URL` is set, otherwise in-memory |
| Admin | Custom `SocialConnectAdminSite` at `/admin/`, not a React route |
| Frontend tests | Vitest/jsdom/testing-library installed but no `npm test` script and no test files found |
| Backend tests | 9 test classes and 65 test methods across five files; current pass/fail output `{u}` |
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
- Production deployment topology, static/media hosting, Redis deployment, email delivery, and monitoring are `{u}`.

## Verification commands from source guidance

From `backend/`:

```powershell
..\\venv\\Scripts\\python.exe manage.py check
..\\venv\\Scripts\\python.exe manage.py makemigrations --check --dry-run
..\\venv\\Scripts\\python.exe manage.py test --keepdb
```

From `frontend/`:

```powershell
npm.cmd run lint
npm.cmd run build
```

`manage.py makemigrations --check --dry-run` was executed during the source audit and returned `No changes detected`. Current results for the other commands are `{u}` unless they are actually run and recorded.

## Status vocabulary

| Status | Meaning |
| --- | --- |
""".format(u=UNVERIFIED)

for name, meaning in VOCAB:
    ANALYSIS += f"| {name} | {meaning} |\n"

write_text(A01 / "Project_Analysis.md", ANALYSIS)

FEATURES = """# Feature Status

Source-oriented implementation status. Screens marked proposed in the visual package are not claimed to exist in the current router.

## Executive summary

| Domain | Overall status | Main caveat |
| --- | --- | --- |
| Identity and access | Implemented with caveats | Username-only login; JWTs in `localStorage`; route guard checks token presence only. |
| Password lifecycle | Partial / Backend only | REST endpoints exist; no dedicated SPA reset/confirm/deactivate screens. |
| Profiles and discovery | Implemented with caveats | Active screen is `UserProfile.jsx`; legacy `Profile.jsx` is unrouted. |
| Posts and feed | Implemented core, several partial extensions | Draft filter contract, pin ordering, scheduling, multi-image upload, polls, reports remain partial/backend-only. |
| Social graph | Implemented core | Block-list management and mutual-friend UI are backend-only; accept/reject notifications absent. |
| Stories | Partial | List/create/view UI exists; reaction UI, edit/delete, and viewed-state persistence are missing. |
| Notifications | Implemented with caveats | REST + WebSocket + preferences UI; read actions do not emit live updates; no pagination. |
| Direct messaging | Implemented with caveats | REST + WebSocket UI; attachment-only sends and message edit/delete controls are missing. |
| Group messaging | Backend only / Partial | REST models/endpoints exist; no group UI or group WebSocket. |
| Custom admin | Implemented with caveats | Real-data dashboard/analytics/roles/system pages; moderation workflow absent. |
| PWA | Partial | App-shell caching only; no offline data, push, install prompt, update flow, or full icon set. |
| Frontend tests | Not Found | Vitest/jsdom installed but no test files or script. |
| Production deployment | Needs Verification / Not Found | Topology, proxy, static/media hosting, Redis runtime, and CI/CD are unverified. |

## Detailed status by area

| Area | Verified capability | Status | Gap / caveat |
| --- | --- | --- | --- |
| Registration and login | `POST /api/users/register/`, `POST /api/users/login/`, SPA forms | Implemented | Generic login catch can swallow explicit invalid-response text. |
| Token refresh and logout | Rotating refresh, blacklist, Axios single-flight refresh | Implemented | Presence-only route guard. |
| Password reset / deactivate | REST endpoints exist | Backend only / Partial | No `/forgot-password` or reset-confirm route. Email delivery `{u}`. |
| Own and public profile | `GET/PATCH /api/users/profile/`, `GET /api/users/<pk>/`, `UserProfile.jsx` | Implemented | Legacy `Profile.jsx` is unrouted. |
| User search and suggestions | `GET /api/users/search/`, right rail | Implemented | No pagination; render-phase URL state sync. |
| Post CRUD and feed | Post endpoints, `GET /api/social/feed/`, home composer/cards | Implemented | Pagination is opt-in via `?page=` only. |
| Drafts and scheduling | `is_draft`, `scheduled_for`, visibility filters | Backend only / Partial | No draft/scheduling UI and no publisher job found. |
| Pinning / reposts / reports | Endpoints and home actions exist | Partial | Pin not consumed by ordering; repost has no notification; reports have no lifecycle. |
| Polls / hashtags / multi-image | Models and partial endpoints | Backend only | No poll composer, hashtag browse endpoint, or `PostImage` writer. |
| Likes / comments / replies | Endpoints and `PostActions.jsx` | Implemented | Comments are not paginated. |
| Follows / friends / blocks | Full REST flows and SPA actions | Implemented with caveats | No block-list screen; no accept/reject notifications. |
| Stories | Create/list/view/view-tracking UI | Partial | No reaction UI, edit/delete, or persisted viewed state. |
| Notifications | List, read, count, preferences, WebSocket | Implemented with caveats | No pagination; read state is not pushed to other clients. |
| Direct chat | Conversation list, history, REST send, WebSocket send/typing/presence/read | Implemented with caveats | No attachment-only send, no edit/delete UI controls, no history pagination. |
| Group chat | Group REST endpoints and models | Backend only / Partial | No group UI and no group WebSocket route. |
| Admin dashboard | 12 KPIs, charts, analytics, roles, system, changelists | Implemented with caveats | Browser smoke result `{u}`; report moderation absent. |
| PWA | Production service worker, manifest | Partial | App shell only; no offline data/push/install/update flow. |
| Frontend automated tests | None found | Not Found | Do not claim frontend tests exist. |
| Product naming | Two names in source | Needs Verification | Final brand `{u}`. |
""".format(u=UNVERIFIED)

write_text(A01 / "Feature_Status.md", FEATURES)

TECH = """# Technology Stack

## Frontend

- React 19.3.1 and React DOM 19.3.1
- React Router 7.18.5
- Axios 1.21.0
- Vite 8.3.6
- Scripts: `dev`, `build`, `lint`, `preview`; no `npm test`
- Active stylesheet: `frontend/src/index.css`; `App.css` exists but is not imported
- Service worker: `frontend/public/sw.js`, registered only in production
- Theme key: `socialconnect-theme`

## Backend

- Django 6.1
- Django REST Framework 3.18.0
- SimpleJWT 5.5.1
- Channels 4.3.2 and channels_redis 4.3.0
- Daphne 4.2.3
- django-cors-headers 4.9.0
- psycopg2-binary 2.9.12
- Pillow 12.3.0
- python-dotenv 1.2.2
- redis 8.1.0

## Runtime topology verified from source

- Browser → Vite dev server during development (default `http://localhost:5173`).
- Browser → Django HTTP API at `http://127.0.0.1:8000/api/` by default, overridable with `VITE_API_BASE_URL`.
- Browser → Django ASGI WebSockets at `ws://127.0.0.1:8000/ws/...` by default, overridable with `VITE_API_ORIGIN`.
- Django → PostgreSQL for all persistent application data and JWT blacklist tables.
- Django Channels → Redis channel layer when `REDIS_URL` is set; otherwise in-memory.
- Django admin at `/admin/` uses custom templates and static assets.

## Environment variables by name only

`DJANGO_SECRET_KEY`, `DEBUG` / `DJANGO_DEBUG`, `ALLOWED_HOSTS`, database credentials, `REDIS_URL`, `FRONTEND_URL`, CORS settings, and email settings are referenced by configuration. No values are reproduced in this package. Runtime values are `{u}`.

## Verification tooling

- Backend: `..\\venv\\Scripts\\python.exe manage.py check`, `makemigrations --check --dry-run`, `test --keepdb`.
- Frontend: `npm.cmd run lint`, `npm.cmd run build`.
- Visual rendering in this package: Python 3 with Pillow for PNG, hand-authored SVG for vector output, standard-library ZIP/XML for XLSX/DOCX, and a direct PDF writer. Mermaid/PlantUML source files are provided as editable diagrams; no external renderer was installed in the checkout.
""".format(u=UNVERIFIED)

write_text(A01 / "Technology_Stack.md", TECH)

TABLES = [
    ("DB-TBL-001", "users_user", "id (BigAutoField), username (unique), email (unique), password, first_name, last_name, is_staff, is_active, is_superuser, date_joined, last_login, email_verified", "AbstractUser; username login; email_verified has no writer"),
    ("DB-TBL-002", "users_profile", "id, user (1-1), profile_picture, cover_photo, bio, location, website, date_of_birth, is_private, allow_comments, allow_messages, is_verified, social_links, education, work, created_at, updated_at", "Auto-created by signal"),
    ("DB-TBL-003", "users_story", "id, author FK, media, text, privacy, expires_at, created_at", "M2M viewers through StoryView; 24-hour expiry"),
    ("DB-TBL-004", "users_storyview", "id, story FK, viewer FK, viewed_at", "Unique (story, viewer)"),
    ("DB-TBL-005", "users_storyreaction", "id, user FK, story FK, reaction_type, created_at, updated_at", "Unique (user, story); seven reaction types"),
    ("DB-TBL-006", "users_adminaction", "id, created_at, action_type, target_type, target_id, target_label, description, metadata", "Inert: no actor, no writer, not admin-registered"),
    ("DB-TBL-007", "posts_post", "id, author FK, content, image, video, audience, is_draft, is_pinned, scheduled_for, repost_of self-FK, created_at, updated_at", "Visibility in social/access.py"),
    ("DB-TBL-008", "posts_postimage", "id, post FK, image, position", "Ordered gallery; no API writer"),
    ("DB-TBL-009", "posts_bookmark", "id, post FK, user FK, created_at", "Unique (post, user)"),
    ("DB-TBL-010", "posts_poll", "id, post OneToOne, question, expires_at", "No poll CRUD endpoint"),
    ("DB-TBL-011", "posts_polloption", "id, poll FK, text", "Vote target"),
    ("DB-TBL-012", "posts_pollvote", "id, option FK, user FK", "Unique (option, user), not (poll, user)"),
    ("DB-TBL-013", "posts_hashtag", "id, name unique", "M2M with Post; regex sync from post text"),
    ("DB-TBL-014", "posts_postreport", "id, post FK, reporter FK, reason, created_at", "No status or resolution field"),
    ("DB-TBL-015", "social_like", "id, post FK, user FK, created_at", "Unique (post, user)"),
    ("DB-TBL-016", "social_comment", "id, post FK, user FK, content, parent self-FK, created_at, updated_at", "Threaded replies"),
    ("DB-TBL-017", "social_mention", "id, comment FK nullable, post FK nullable, mentioned FK, created_at", "No exclusive-or DB constraint"),
    ("DB-TBL-018", "social_commentreaction", "id, comment FK, user FK, reaction, created_at", "Unique (comment, user); no UI"),
    ("DB-TBL-019", "social_follow", "id, follower FK, following FK, created_at", "Unique directional pair"),
    ("DB-TBL-020", "social_block", "id, blocker FK, blocked FK, created_at", "Unique pair; DB self-block check; index on blocker/created_at"),
    ("DB-TBL-021", "social_friendrequest", "id, sender FK, receiver FK, status, created_at, updated_at", "Unique direction; status pending/accepted/rejected; self-request check"),
    ("DB-TBL-022", "notifications_notification", "id, recipient FK, sender FK, notification_type, post FK nullable, comment FK nullable, is_read, created_at", "IDs masked when target is not visible"),
    ("DB-TBL-023", "notifications_notificationpreference", "id, user OneToOne, likes, comments, replies, follows, friend_requests, messages, mentions, story_reactions", "Eight opt-out booleans"),
    ("DB-TBL-024", "chat_groupconversation", "id, name, avatar, created_by FK, created_at", "M2M members through GroupMembership"),
    ("DB-TBL-025", "chat_groupmembership", "id, group FK, user FK, role, muted, archived", "Unique (group, user); role/mute/archive unused in source"),
    ("DB-TBL-026", "chat_message", "id, sender FK, receiver FK nullable, group FK nullable, content, attachment, edited_at, deleted_at, is_read, created_at", "Soft delete; no exclusive-or DB constraint"),
]

RELATIONSHIPS = [
    ("User", "Profile", "1—1", "user"),
    ("User", "Post", "1—N", "author"),
    ("User", "Story", "1—N", "author"),
    ("Story", "User", "M—N", "viewers through StoryView"),
    ("Story", "StoryReaction", "1—N", "reactions"),
    ("Post", "PostImage", "1—N", "images"),
    ("Post", "Poll", "1—1", "poll"),
    ("Poll", "PollOption", "1—N", "options"),
    ("PollOption", "PollVote", "1—N", "votes"),
    ("Post", "Hashtag", "M—N", "hashtags"),
    ("Post", "Comment", "1—N", "comments"),
    ("Comment", "Comment", "1—N", "parent replies"),
    ("Post", "Like", "1—N", "likes"),
    ("User", "Follow", "1—N", "follower/following"),
    ("User", "Block", "1—N", "blocker/blocked"),
    ("User", "FriendRequest", "1—N", "sender/receiver"),
    ("Notification", "User", "N—1", "recipient/sender"),
    ("User", "NotificationPreference", "1—1", "notification_preferences"),
    ("GroupConversation", "User", "M—N", "members through GroupMembership"),
    ("Message", "User", "N—1", "sender/receiver"),
    ("Message", "GroupConversation", "N—1", "group"),
]

dd = ["# Data Dictionary\n\nSource: current Django model and migration files. Primary keys are implicit BigAutoField IDs unless stated. Privacy is enforced in application query layers, not database row-level security.\n\n## Tables\n\n| ID | Table | Attributes | Notes |\n| --- | --- | --- | --- |\n"]
for rid, table, attrs, note in TABLES:
    dd.append(f"| {rid} | `{table}` | {attrs} | {note} |\n")
dd.append("\n## Relationship summary\n\n| Parent | Child | Cardinality | Key / through |\n| --- | --- | --- | --- |\n")
for a, b, card, key in RELATIONSHIPS:
    dd.append(f"| `{a}` | `{b}` | {card} | {key} |\n")
dd.append(
    "\n## Constraints and application-level invariants\n\n"
    "- Unique pairs: profile↔user, story view, story reaction, bookmark, like, comment reaction, follow direction, block direction, friend-request direction, group membership.\n"
    "- DB check constraints: `block_not_self`, `friend_request_not_self`.\n"
    "- View-level invariants: one vote per poll per user, post visibility/audience, self-action guards, message target construction, soft-delete filtering, story expiry/privacy.\n"
    "- Known gaps: `PostReport` has no status; `PollVote` uniqueness is per option only; `Message` has no exclusive receiver/group constraint; `PostImage` has no writer; `Mention` has no exclusive target constraint.\n"
    "- `django.contrib.admin.models.LogEntry` is the actual admin activity source. `AdminAction` is dormant.\n\n"
    "- Migration alignment: `manage.py makemigrations --check --dry-run` returned `No changes detected`; applied runtime state is " + UNVERIFIED + ".\n"
)
write_text(A04 / "Data_Dictionary.md", "".join(dd))

# Requirements and traceability data -------------------------------------------------

REQS = [
    ("UR-001", "Register account", "Guest", "UI-SCR-002", "Register.jsx", "users/views.py", "API-010", "users_user, users_profile", "F-001", "TC-001", "Implemented"),
    ("UR-002", "Login and receive JWT", "Guest", "UI-SCR-001", "Login.jsx", "users/views.py", "API-011", "users_user", "F-002", "TC-002", "Implemented"),
    ("UR-003", "Refresh access token", "Registered User", "Global API client", "api/axios.js", "users/views.py", "API-012", "users_user", "F-003", "TC-003", "Implemented"),
    ("UR-004", "Logout / blacklist refresh", "Registered User", "Navbar account menu", "navbar.jsx", "users/views.py", "API-013", "users_user", "F-004", "TC-004", "Implemented"),
    ("UR-005", "Request password reset", "Guest", "No SPA route (proposed mockup)", "Proposed: ForgotPassword", "users/views.py", "API-015", "users_user", "F-006", "TC-005", "Backend only"),
    ("UR-006", "Confirm password reset", "Guest", "No SPA route", "Not found", "users/views.py", "API-016", "users_user", "F-007", "TC-006", "Backend only"),
    ("UR-007", "Deactivate account", "Registered User", "No SPA screen", "Not found", "users/views.py", "API-017", "users_user", "F-008", "TC-007", "Backend only"),
    ("UR-008", "Edit own profile and privacy", "Registered User", "UI-SCR-007", "EditProfile.jsx", "users/views.py", "API-018, API-019", "users_profile", "F-011", "TC-008", "Implemented"),
    ("UR-009", "Search and discover people", "Registered User", "UI-SCR-008", "UserSearch.jsx", "users/views.py", "API-020", "users_user, users_profile", "F-015", "TC-009", "Implemented"),
    ("UR-010", "View public profile", "Registered User", "UI-SCR-006", "UserProfile.jsx", "users/views.py", "API-027, API-028", "users_user, users_profile", "F-012", "TC-010", "Implemented"),
    ("UR-011", "Create/edit/delete post", "Content Author", "UI-SCR-003", "home.jsx", "posts/views.py", "API-031, API-032", "posts_post", "F-019", "TC-011", "Implemented"),
    ("UR-012", "Browse filtered feed", "Registered User", "UI-SCR-003", "home.jsx", "social/views.py, social/access.py", "API-040", "posts_post, social_block", "F-020", "TC-012", "Implemented"),
    ("UR-013", "Like post", "Registered User", "UI-SCR-003, UI-SCR-005", "PostActions.jsx", "social/views.py", "API-041", "social_like", "F-034", "TC-013", "Implemented"),
    ("UR-014", "Comment and reply", "Registered User", "UI-SCR-005", "PostActions.jsx", "social/views.py", "API-042, API-043", "social_comment", "F-035, F-036", "TC-014", "Implemented"),
    ("UR-015", "Bookmark post", "Registered User", "UI-SCR-011", "Bookmarks.jsx", "posts/views.py", "API-033", "posts_bookmark", "F-028", "TC-015", "Implemented"),
    ("UR-016", "Pin / repost / report post", "Content Author / Registered User", "UI-SCR-003", "home.jsx", "posts/views.py", "API-034, API-035, API-037", "posts_post, posts_postreport", "F-026, F-027, F-031", "TC-016", "Partial"),
    ("UR-017", "Create and view story", "Registered User", "UI-SCR-004", "Stories.jsx", "users/views.py", "API-021, API-022, API-023", "users_story, users_storyview", "F-045, F-046, F-047", "TC-017", "Implemented"),
    ("UR-018", "React to story", "Registered User", "No reaction control", "Not found", "users/views.py", "API-024, API-026", "users_storyreaction", "F-049", "TC-018", "Backend only"),
    ("UR-019", "Follow / unfollow user", "Registered User", "UI-SCR-006, UI-SCR-008", "UserProfile.jsx, UserSearch.jsx", "social/views.py", "API-046, API-047", "social_follow", "F-040", "TC-019", "Implemented"),
    ("UR-020", "Send/accept/reject friend request", "Registered User", "UI-SCR-009", "FriendRequests.jsx", "social/views.py", "API-048—API-052", "social_friendrequest", "F-042", "TC-020", "Partial"),
    ("UR-021", "Block / unblock user", "Registered User", "UI-SCR-006", "UserProfile.jsx", "social/views.py", "API-059, API-060", "social_block", "F-044", "TC-021", "Partial"),
    ("UR-022", "Manage notification preferences", "Registered User", "Notification settings dialog", "NotificationSettingsDialog.jsx", "notifications/views.py", "API-074, API-075", "notifications_notificationpreference", "F-054", "TC-022", "Implemented"),
    ("UR-023", "Read notifications and counts", "Registered User", "UI-SCR-013", "Notifications.jsx", "notifications/views.py", "API-070—API-073", "notifications_notification", "F-051, F-053", "TC-023", "Implemented"),
    ("UR-024", "Send direct message", "Message Participant", "UI-SCR-012", "Messages.jsx", "chat/views.py, chat/consumers.py", "API-081, API-082, API-090", "chat_message", "F-059, F-060", "TC-024", "Implemented"),
    ("UR-025", "Send typing/presence/read events", "Message Participant", "UI-SCR-012", "Messages.jsx", "chat/consumers.py, chat/views.py", "API-083, API-090", "chat_message", "F-061, F-062", "TC-025", "Implemented"),
    ("UR-026", "Create group conversation", "Group Member", "No SPA screen", "Not found", "chat/views.py", "API-087, API-088", "chat_groupconversation, chat_groupmembership", "F-064", "TC-026", "Backend only"),
    ("UR-027", "Send group message", "Group Member", "No SPA screen", "Not found", "chat/views.py", "API-089", "chat_message", "F-064", "TC-027", "Backend only"),
    ("UR-028", "Vote in poll", "Registered User", "No SPA control", "Not found", "posts/views.py", "API-036", "posts_pollvote", "F-030", "TC-028", "Backend only"),
    ("UR-029", "Submit post report", "Registered User", "UI-SCR-003", "home.jsx", "posts/views.py", "API-037", "posts_postreport", "F-031", "TC-029", "Partial"),
    ("UR-030", "Review admin analytics", "Admin", "Admin analytics page", "Django template", "config/admin_site.py, admin_metrics.py", "API-002", "Django aggregates", "F-068", "TC-030", "Implemented"),
    ("UR-031", "Manage users via admin actions", "Admin", "Django admin changelist", "Django template", "users/admin.py", "API-002", "users_user", "F-065", "TC-031", "Implemented"),
    ("UR-032", "View system status", "Admin", "Admin system page", "Django template", "config/admin_site.py", "API-002", "Django LogEntry", "F-070, F-071", "TC-032", "Implemented"),
    ("UR-033", "Persist JWT session in browser storage", "Registered User", "Global session state", "api/axios.js", "users/views.py", "API-011, API-012", "None", "F-003", "TC-033", "Implemented"),
    ("UR-034", "Use light/dark theme", "Registered User", "Navbar / admin theme toggle", "navbar.jsx, admin JS", "Static CSS/JS", "None", "None", "F-074", "TC-034", "Implemented"),
    ("UR-035", "Cache only the app shell offline", "Registered User", "PWA shell", "main.jsx, public/sw.js", "Static files", "None", "None", "F-073", "TC-035", "Partial"),
]

NFR = [
    ("NFR-001", "Authentication", "HTTP requests use bearer access tokens; WebSocket connections use query-string access tokens."),
    ("NFR-002", "Token lifecycle", "Refresh tokens rotate and blacklisting is enabled; the SPA refreshes once on 401."),
    ("NFR-003", "Privacy", "Audience, block, private-profile, and story-expiry filters are applied in application query layers."),
    ("NFR-004", "Notification delivery", "Notifications are persisted before `on_commit` channel publication; preferences and blocks are checked centrally."),
    ("NFR-005", "Real-time transport", "ASGI/Daphne is required; Redis is needed for multi-process WebSocket fan-out."),
    ("NFR-006", "Performance", "Home feed supports opt-in pagination; most other SPA lists render the first response only."),
    ("NFR-007", "Accessibility", "Dialogs, tabs, switches, keyboard navigation, focus traps, and reduced-motion handling exist; several form-label gaps remain."),
    ("NFR-008", "Responsiveness", "CSS breakpoints support desktop, tablet, mobile, and very small screens."),
    ("NFR-009", "Security", "LocalStorage tokens and query-string WebSocket tokens are documented risks; media URLs are not authorization-aware."),
    ("NFR-010", "Observability", "Admin system page reports DB connectivity and configuration facts; no Redis ping or socket handshake is performed."),
    ("NFR-011", "Verification", "Backend tests exist; frontend tests are not found. Current command results are " + UNVERIFIED + "."),
    ("NFR-012", "Deployment", "Production topology, proxy, TLS, static/media hosting, CI/CD, and monitoring are " + UNVERIFIED + "."),
]

req_md = ["# User Requirements\n\nIDs are stable across the visual package. `UR` identifies a user-facing requirement, `FR` references the source-derived feature ID from `FEATURE_IMPLEMENTATION_MATRIX.md`, and `NFR` identifies a non-functional requirement.\n\n## Functional requirements\n\n| ID | Requirement | Primary actor | Source feature | Status |\n| --- | --- | --- | --- | --- |\n"]
for r in REQS:
    req_md.append(f"| {r[0]} | {r[1]} | {r[2]} | {r[8]} | {r[10]} |\n")
req_md.append("\n## Non-functional requirements\n\n| ID | Category | Requirement |\n| --- | --- | --- |\n")
for n in NFR:
    req_md.append(f"| {n[0]} | {n[1]} | {n[2]} |\n")
req_md.append(
    "\n## Requirement handling rules\n\n"
    "- Proposed mockups for password reset, explore/settings-style screens, story reactions, user dashboard, and user reporting are visual proposals only; they do not convert backend-only features into implemented requirements.\n"
    "- Requirements marked Backend only or Partial keep that status in every diagram and matrix.\n"
    "- No new route, model, endpoint, workflow, or test result is invented.\n"
    "- Unresolved runtime and product decisions retain the exact marker " + UNVERIFIED + ".\n"
)
write_text(A08 / "User_Requirements.md", "".join(req_md))

TEST_PLAN = """# Test Plan

## Scope

This plan is source-derived. It describes what should be verified for the documented requirements; it does not claim that any command currently passes. Current results for backend tests, frontend lint, frontend build, and browser smoke checks are `{u}` unless executed and recorded.

## Verification commands

```powershell
# backend/
..\\venv\\Scripts\\python.exe manage.py check
..\\venv\\Scripts\\python.exe manage.py makemigrations --check --dry-run
..\\venv\\Scripts\\python.exe manage.py test --keepdb

# frontend/
npm.cmd run lint
npm.cmd run build
```

`makemigrations --check --dry-run` was executed during the source audit and returned `No changes detected`.

## Test levels

| Level | Source evidence | Coverage focus |
| --- | --- | --- |
| Model/schema | 26 Django tables; migrations for users/posts/social/notifications/chat | Constraints, soft delete, relationships, migration alignment |
| API | DRF APIView/generics endpoints under five prefixes | Auth, ownership, visibility, toggles, state transitions, error codes |
| WebSocket | Channels `WebsocketCommunicator` tests against `config.asgi.application` | JWT close codes, chat events, notification delivery |
| Frontend | No test files or `npm test` script found | Lint/build only; interaction tests are proposed, not existing |
| Admin | Custom admin views and metrics | Permission masking, range normalization, KPI aggregation, activity source |
| Browser/UX | No verified smoke results in source | Responsive layout, focus traps, dialogs; `{u}` |

## Proposed test cases

Test IDs below are proposals for the documentation package, not claims of existing test methods.

| ID | Requirement | Objective | Expected source-aligned result |
| --- | --- | --- | --- |
""".format(u=UNVERIFIED)

for r in REQS:
    rid, title, actor, screen, component, module, api, model, feature, tc, status = r
    objective = f"Verify {title.lower()} for {actor.lower()} using {screen}."
    expected = f"Source-aligned behavior for {status}; API {api}; models {model}."
    TEST_PLAN += f"| {tc} | {rid} | {objective} | {expected} |\n"

TEST_PLAN += """
## Risks and exclusions

- Do not assert a current pass count from historical reports.
- No frontend automated tests exist to run.
- No production deployment, email delivery, Redis runtime, or media authorization test was verified.
- Concurrency and raw-ORM constraint tests were not found; proposed cases should be added only if approved.
"""

write_text(A10 / "Test_Plan.md", TEST_PLAN)


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def col_name(i: int) -> str:
    name = ""
    while i >= 0:
        name = chr(65 + i % 26) + name
        i = i // 26 - 1
    return name


def sheet_xml(headers: list[str], rows: list[list[object]]) -> str:
    out = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>', '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">']
    out.append("<cols>")
    for i, header in enumerate(headers):
        width = min(60, max(14, len(header) + 6))
        out.append(f'<col min="{i + 1}" max="{i + 1}" width="{width}" customWidth="1"/>')
    out.append("</cols><sheetData>")
    all_rows = [headers] + rows
    for ri, row in enumerate(all_rows, start=1):
        out.append(f'<row r="{ri}">')
        for ci, value in enumerate(row):
            ref = f"{col_name(ci)}{ri}"
            out.append(f'<c r="{ref}" t="inlineStr"><is><t xml:space="preserve">{esc(value)}</t></is></c>')
        out.append("</row>")
    out.append("</sheetData></worksheet>")
    return "".join(out)


def write_xlsx(path: Path, sheets: list[tuple[str, list[str], list[list[object]]]]) -> None:
    content_types = [
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">',
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>',
        '<Default Extension="xml" ContentType="application/xml"/>',
        '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>',
    ]
    for i in range(len(sheets)):
        content_types.append(f'<Override PartName="/xl/worksheets/sheet{i + 1}.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>')
    content_types.append("</Types>")

    workbook = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>', '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets>']
    rels = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>', '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">']
    for i, (name, _, _) in enumerate(sheets):
        workbook.append(f'<sheet name="{esc(name)}" sheetId="{i + 1}" r:id="rId{i + 1}"/>')
        rels.append(f'<Relationship Id="rId{i + 1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet{i + 1}.xml"/>')
    workbook.append("</sheets></workbook>")
    rels.append("</Relationships>")

    root_rels = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>'

    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", "".join(content_types))
        z.writestr("_rels/.rels", root_rels)
        z.writestr("xl/workbook.xml", "".join(workbook))
        z.writestr("xl/_rels/workbook.xml.rels", "".join(rels))
        for i, (_, headers, rows) in enumerate(sheets):
            z.writestr(f"xl/worksheets/sheet{i + 1}.xml", sheet_xml(headers, rows))


trace_headers = ["UR ID", "Requirement", "FR / feature ID", "Actor", "UI screen", "React component", "Django module", "API ID", "DB model", "Status", "Proposed TC", "Evidence note"]
trace_rows = []
for r in REQS:
    rid, title, actor, screen, component, module, api, model, feature, tc, status = r
    evidence = "Source-verified; test case proposal only" if status != "Needs Verification" else UNVERIFIED
    trace_rows.append([rid, title, feature, actor, screen, component, module, api, model, status, tc, evidence])
write_xlsx(A09 / "Requirements_Traceability.xlsx", [("Traceability", trace_headers, trace_rows)])

test_headers = ["TC ID", "UR ID", "Objective", "Type", "Preconditions", "Steps", "Expected result", "Status"]
test_rows = []
for r in REQS:
    rid, title, actor, screen, component, module, api, model, feature, tc, status = r
    steps = f"1. Open {screen}. 2. Exercise {title.lower()}. 3. Inspect API/model state."
    expected = f"Behavior matches source-verified status: {status}. API: {api}. Models: {model}."
    test_rows.append([tc, rid, f"Verify {title.lower()}", "Proposed functional", f"Valid {actor.lower()} session unless public", steps, expected, "Proposed / " + status])
write_xlsx(A10 / "Test_Cases.xlsx", [("Test Cases", test_headers, test_rows)])

print("generated analysis, requirements, data dictionary, and spreadsheets")

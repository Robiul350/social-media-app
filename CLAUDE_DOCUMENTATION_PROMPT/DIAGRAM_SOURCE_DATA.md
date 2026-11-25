# Diagram Source Data

 curated, source-verified inputs for generating UML, ER, sequence, activity, state, component, and deployment diagrams. Use the IDs below consistently across all deliverables. Do not add entities, actors, states, events, or deployment nodes that are not listed here unless the user explicitly approves them.

Legend for generated diagrams:

- REST endpoints are all `APIView`/`generics`/SimpleJWT views; there are no ViewSets or `@action` decorators.
- **Verified** — present in current source.
- **Partial** — code exists but flow/lifecycle is incomplete.
- **Backend only** — no reachable SPA/admin surface found.
- `[NOT VERIFIED - USER CONFIRMATION REQUIRED]` — unresolved; reproduce verbatim in the diagram.

---

## 1. Actors

| Actor ID | Actor | Verified interactions |
| --- | --- | --- |
| ACT-001 | Guest | Register, login, view API root. |
| ACT-002 | Registered User | Profile, feed, posts, likes/comments, follows/friends/blocks, stories, notifications, direct chat. |
| ACT-003 | Content Author | Create/edit/delete own posts, drafts, audience selection, pin, repost, report others' posts. |
| ACT-004 | Friend / Follower | Friend requests, visible friend/follower-only content, messaging eligibility. |
| ACT-005 | Story Viewer | View visible stories, track views; reaction capability is backend only in SPA. |
| ACT-006 | Message Participant | Direct conversation, typing, presence, read receipts, attachments. |
| ACT-007 | Group Member | Backend-only group creation and group message REST operations. |
| ACT-008 | Moderator / Admin | Django admin dashboard, analytics, model changelists, roles/system views. No SPA moderation screen. |
| ACT-009 | External System | PostgreSQL, optional Redis channel layer, email delivery, media storage. Email delivery success is `[NOT VERIFIED - USER CONFIRMATION REQUIRED]`. |

---

## 2. Use cases

| UC ID | Use case | Primary actor | Status | Evidence |
| --- | --- | --- | --- | --- |
| UC-001 | Register account | Guest | Implemented | `users/views.py`, `Register.jsx` |
| UC-002 | Login and receive JWT | Guest | Implemented | `users/views.py`, `Login.jsx`, `api/axios.js` |
| UC-003 | Refresh access token | Registered User | Implemented | `users/views.py`, Axios interceptor |
| UC-004 | Logout / blacklist refresh | Registered User | Implemented | `users/views.py`, navbar |
| UC-005 | Request password reset | Guest | Backend only / Partial | `users/views.py`; no SPA route |
| UC-006 | Confirm password reset | Guest | Backend only / Partial | `users/views.py`; no SPA route |
| UC-007 | Deactivate account | Registered User | Backend only | `users/views.py`; no SPA screen |
| UC-008 | Edit own profile and privacy | Registered User | Implemented | `users/views.py`, `EditProfile.jsx` |
| UC-009 | Search and discover people | Registered User | Implemented | `users/views.py`, `UserSearch.jsx` |
| UC-010 | View public profile | Registered User | Implemented | `users/views.py`, `UserProfile.jsx` |
| UC-011 | Create/edit/delete post | Content Author | Implemented | `posts/views.py`, `home.jsx` |
| UC-012 | Browse filtered feed | Registered User | Implemented | `social/views.py`, `social/access.py`, `home.jsx` |
| UC-013 | Like post | Registered User | Implemented | `social/views.py`, `PostActions.jsx` |
| UC-014 | Comment and reply | Registered User | Implemented | `social/views.py`, `PostActions.jsx` |
| UC-015 | Bookmark post | Registered User | Implemented | `posts/views.py`, `Bookmarks.jsx` |
| UC-016 | Pin / repost / report post | Content Author / Registered User | Partial | `posts/views.py`, `home.jsx` |
| UC-017 | Create and view story | Registered User | Implemented | `users/views.py`, `Stories.jsx` |
| UC-018 | React to story | Registered User | Backend only | `users/views.py`; no reaction UI |
| UC-019 | Follow / unfollow user | Registered User | Implemented | `social/views.py`, profile/search |
| UC-020 | Send/accept/reject friend request | Registered User | Implemented with caveats | `social/views.py`, `FriendRequests.jsx` |
| UC-021 | Block / unblock user | Registered User | Implemented effect / Partial UI | `social/views.py`, `UserProfile.jsx` |
| UC-022 | Manage notification preferences | Registered User | Implemented | `notifications/views.py`, settings dialog |
| UC-023 | Read notifications and counts | Registered User | Implemented | `notifications/views.py`, `Notifications.jsx` |
| UC-024 | Send direct message | Message Participant | Implemented | `chat/views.py`, `chat/consumers.py`, `Messages.jsx` |
| UC-025 | Send typing/presence/read events | Message Participant | Implemented | chat consumer/REST read |
| UC-026 | Create group conversation | Group Member | Backend only / Partial | `chat/views.py`; no SPA UI |
| UC-027 | Send group message | Group Member | Backend only / Partial | `chat/views.py`; no group WS |
| UC-028 | Vote in poll | Registered User | Backend only | `posts/views.py`; no UI |
| UC-029 | Submit post report | Registered User | Partial | `posts/views.py`, `home.jsx`; no moderation lifecycle |
| UC-030 | Review admin analytics | Admin | Implemented | `config/admin_site.py`, `admin_metrics.py` |
| UC-031 | Manage users via admin actions | Admin | Implemented | `users/admin.py` deactivate/reactivate actions |
| UC-032 | Mark notifications read via admin | Admin | Implemented | `notifications/admin.py` actions |
| UC-033 | View system status | Admin | Implemented | `config/admin_site.py`, `admin_system.html` |

---

## 3. Entities and relationships for class/ER diagrams

Use the `DB-TBL-*` IDs from `DATABASE_ANALYSIS.md`.

| Entity | Key relationships |
| --- | --- |
| `User` (DB-TBL-001) | 1—1 `Profile`; 1—N `Post`, `Story`, `Like`, `Comment`, `Follow`, `Block`, `FriendRequest`, `Bookmark`, `PollVote`, `StoryView`, `StoryReaction`, `CommentReaction`, `Mention`, `Notification`, `Message`, `GroupMembership`, `GroupConversation.created_by`. |
| `Profile` (002) | Owned by exactly one `User`. |
| `Story` (003) | Author `User`; M2M viewers through `StoryView`; 1—N `StoryReaction`. |
| `StoryView` (004) | `Story` + `viewer User`; unique pair. |
| `StoryReaction` (005) | `Story` + `user User`; unique pair; one of seven reaction types. |
| `AdminAction` (006) | Inert; no actor, no writer. |
| `Post` (007) | Author `User`; 1—N `PostImage`, `Like`, `Comment`, `Bookmark`, `PostReport`; 1—1 `Poll`; self-referential `repost_of`; M2M `Hashtag`. |
| `PostImage` (008) | Belongs to `Post`; ordered by `position`; no API writer. |
| `Bookmark` (009) | `Post` + `user`; unique pair. |
| `Poll` (010) | One-to-one with `Post`; 1—N `PollOption`. |
| `PollOption` (011) | Belongs to `Poll`; 1—N `PollVote`. |
| `PollVote` (012) | `option` + `user`; unique per option only. |
| `Hashtag` (013) | M2M with `Post`; unique name. |
| `PostReport` (014) | `post` + `reporter`; no status field. |
| `Like` (015) | `post` + `user`; unique pair. |
| `Comment` (016) | `post` + `user`; self-referential `parent`; 1—N `Mention`, `CommentReaction`. |
| `Mention` (017) | Optional `comment`/`post` + `mentioned User`. |
| `CommentReaction` (018) | `comment` + `user`; unique pair. |
| `Follow` (019) | `follower` + `following`; unique directional pair. |
| `Block` (020) | `blocker` + `blocked`; unique pair; self-block check constraint. |
| `FriendRequest` (021) | `sender` + `receiver`; status lifecycle `pending/accepted/rejected`; self-request check constraint. |
| `Notification` (022) | `recipient` + `sender`; optional `post`/`comment`; type enum. |
| `NotificationPreference` (023) | One-to-one with `User`; eight boolean toggles. |
| `GroupConversation` (024) | `created_by User`; M2M `members` through `GroupMembership`; 1—N `Message` via `group`. |
| `GroupMembership` (025) | `group` + `user`; role/muted/archived; unique pair. |
| `Message` (026) | `sender`; optional direct `receiver` or `group`; soft-delete via `deleted_at`; attachment. |

---

## 4. Sequence diagram inputs

### SEQ-001 — Registration and login

1. Guest submits registration form → `POST /api/users/register/`.
2. API validates password, creates `User`, signal creates `Profile`.
3. Guest submits login → `POST /api/users/login/`.
4. API authenticates username/password, issues access + refresh.
5. SPA stores four localStorage keys and dispatches auth-change.
6. On later 401, Axios refreshes via `POST /api/users/token/refresh/`, replaces tokens, replays request.

### SEQ-002 — Create post with audience and media

1. Author selects text/media/audience in home composer.
2. SPA sends multipart `POST /api/posts/`.
3. Serializer validates content/media and file sizes.
4. View sets author, syncs hashtags from content, applies draft/scheduled flags.
5. API returns `PostSerializer`; SPA refreshes feed or prepends post.

### SEQ-003 — Like and comment with notifications

1. User clicks like or submits comment/reply.
2. API checks visibility and block policy via `social/access.py`.
3. Like/comment row is created or toggled.
4. `create_notification()` skips self/blocked recipients, checks preference, persists `Notification`, and on commit publishes to `notifications_<recipient_id>`.
5. Notification consumer pushes event to recipient SPA.

### SEQ-004 — Follow or friend request

1. User acts from profile/search/right rail.
2. API checks self/block/relationship conflicts.
3. `Follow` or `FriendRequest` created/toggled.
4. Follow/send-request notification is created through the central utility.
5. Accept/reject updates `FriendRequest.status`; no notification is emitted for these transitions.

### SEQ-005 — Story list, view, and reaction

1. SPA calls `GET /api/users/stories/`.
2. API filters by expiry, privacy, private author profile, and blocks.
3. Viewer opens story → `POST /api/users/stories/<id>/view/`; unique `StoryView` row.
4. Backend reaction endpoint can create/update `StoryReaction` and emits notification on every POST.
5. SPA viewer has no reaction control, so steps 4 exists as backend-only branch.

### SEQ-006 — Direct message via REST and WebSocket

1. Sender opens `/messages/<user_id>/`; SPA calls conversation history REST endpoint.
2. Opening conversation calls read endpoint; API broadcasts `read_receipt`.
3. Sender sends text over WebSocket or attachment via REST `FormData`.
4. Consumer/view rechecks `can_chat_between`, persists `Message`, creates notification, broadcasts to deterministic direct-chat group.
5. Receiver SPA renders `chat_message`; it also handles `typing`, `presence`, `read_receipt`, `message_updated`, `message_deleted`, and `error` frames.
6. REST edit/delete broadcasts `message_updated`/`message_deleted` for direct messages; no SPA trigger controls exist.

### SEQ-007 — Notification creation and delivery

1. Domain view calls `create_notification(recipient, sender, type, post/comment)`.
2. Utility skips self and blocked recipients; checks `NotificationPreference`.
3. Persists `Notification`.
4. `transaction.on_commit` sends `notification.created` to channel layer group.
5. `NotificationConsumer` translates it to the client frame `{"type":"notification","notification":...}` and forwards it to the recipient socket.
6. SPA prepends notification and refreshes unread counts locally.
7. Marking read updates DB/local state only; no live update to other clients.

### SEQ-008 — Admin analytics request

1. Admin opens `/admin/analytics/?range=7|30|90`.
2. `admin_site.analytics_view()` checks staff and one of eight model permissions.
3. `normalize_range()` falls back to 30 for invalid input.
4. `build_analytics()` queries real tables for daily/monthly series, totals, and ranked tables.
5. Permission masking replaces restricted values/charts.
6. Template embeds JSON via `json_script`; client JS draws canvas charts with no fetch calls.

---

## 5. Activity diagram inputs

### ACTV-001 — Route guard and token refresh

- `access` present? No → `/login`.
- API returns 401 → refresh once → success: retry and keep session; failure: clear four localStorage keys, dispatch auth-change, redirect to `/login`.

### ACTV-002 — Feed visibility

- Exclude drafts unless author's `drafts=true` path.
- Exclude future scheduled posts.
- Apply audience: `public`, `followers`, `friends`.
- Apply private-profile rules and block filtering via `social/access.py`.
- If `?page=` present, return paginated object; otherwise bare array.

### ACTV-003 — Comment creation

- Validate target post visibility and comment permission.
- Validate `parent` belongs to same post and no cycle.
- Create comment; extract `@mentions`; notify post author or parent comment author.
- Mention regex can capture trailing punctuation, producing invalid lookup.

### ACTV-004 — Report lifecycle

- Submit `reason` → create `PostReport`.
- No status field, no resolve/reject endpoint, no moderation UI.
- Admin dashboard counts reports as submissions only.

### ACTV-005 — Story visibility/expiry

- Exclude `expires_at <= now`.
- Apply story privacy (`public/followers/friends`) and author's private-profile state.
- Exclude blocked users.
- View records a unique `(story,viewer)` row.

---

## 6. State machine data

| State ID | Object | States | Transitions | Source |
| --- | --- | --- | --- | --- |
| STATE-001 | `FriendRequest` | `pending`, `accepted`, `rejected` | Send → pending; accept → accepted; reject → rejected; delete cancels pending only. No notification on accept/reject. | `social/models.py`, `social/views.py` |
| STATE-002 | `Notification` | `unread`, `read` | Create → `is_read=False`; mark-one/read-all → `is_read=True`; no reverse flow in API; no WS read update. | `notifications/models.py`, `views.py` |
| STATE-003 | `Message` | `active`, `edited`, `soft-deleted` | Send → active; PATCH → `edited_at` set; DELETE → `deleted_at` set; reads exclude deleted. | `chat/models.py`, `views.py` |
| STATE-004 | `Post` | `draft`, `scheduled`, `published` (as represented by flags/fields) | `is_draft=True` → draft; `scheduled_for` in future → hidden; otherwise visible. No publisher job found; pinning/reposting are orthogonal flags. | `posts/models.py`, `posts/views.py`, `social/access.py` |
| STATE-005 | JWT session | `anonymous`, `authenticated`, `refreshing`, `expired/cleared` | Login → authenticated; 401 → refreshing; refresh success → authenticated; failure/logout → cleared. | `api/axios.js`, `users/views.py` |

---

## 7. Component diagram data

| Component ID | Node | Responsibility |
| --- | --- | --- |
| COMP-001 | React SPA | Pages, components, router, theme, dialogs, media viewer. |
| COMP-002 | Axios API client | Bearer injection, single-flight 401 refresh, session clearing, media URL resolution. |
| COMP-003 | Profile store | External store cache with subscription. |
| COMP-004 | WebSocket clients | Chat and notification sockets with reconnect/backoff. |
| COMP-005 | Browser service worker | Production-only app-shell precache; network-first navigation fallback. |
| COMP-006 | Django HTTP app / DRF | Five API prefixes, serializers, permissions, domain views. |
| COMP-007 | `social/access.py` | Visibility, audience, private-profile, block, chat-policy helpers. |
| COMP-008 | `notifications/utils.py` | Preference/block-aware notification creation and on-commit publish. |
| COMP-009 | Channels consumers | Direct chat and notification WebSocket protocols. |
| COMP-010 | Custom Django admin | Dashboard, analytics, roles, system, model changelists. |
| COMP-011 | PostgreSQL | System of record and SimpleJWT blacklist tables. |
| COMP-012 | Channel layer | Redis when `REDIS_URL` set; otherwise in-memory. |
| COMP-013 | Media storage | `MEDIA_ROOT` filesystem paths; production host `[NOT VERIFIED - USER CONFIRMATION REQUIRED]`. |
| COMP-014 | Email service | Password-reset link delivery; configuration/success `[NOT VERIFIED - USER CONFIRMATION REQUIRED]`. |

---

## 8. Deployment diagram data

Verified from source/README:

- Browser accesses Vite dev server for SPA during development (`http://localhost:5173` default).
- Browser accesses Django API at `http://127.0.0.1:8000/api/` by default; overridden via `VITE_API_BASE_URL`.
- WebSockets use `ws://127.0.0.1:8000/ws/...` by default; origin overridden via `VITE_API_ORIGIN`.
- ASGI application is `config.asgi:application`; Daphne is documented for WebSocket support.
- PostgreSQL is mandatory.
- Redis is optional locally but required for multi-process WebSocket fan-out.
- Root `.env` supplies configuration; values must never be documented.

Unverified / user confirmation required:

- Reverse proxy, TLS termination, production domain, production SPA host, static files strategy, media serving strategy, worker count, process supervisor, monitoring, logging pipeline, CI/CD, Redis deployment, email provider, and backup strategy are all `[NOT VERIFIED - USER CONFIRMATION REQUIRED]`.

---

## 9. Naming and labeling rules for diagrams

- Use `Social Media App (working UI/admin name: SocialConnect)` in titles until the official name is confirmed.
- Use the exact status vocabulary: Implemented, Partial, Backend only, Planned / documented, Not Found, Needs Verification.
- Use `API-xxx` labels on endpoints, `DB-TBL-xxx` on tables, `UC-xxx` on use cases, `UI-SCR-xxx` on screens, and `FR-xxx`/`NFR-xxx` when tracing requirements.
- Do not draw a moderator workflow beyond report submission and admin report listing; no status/resolve workflow exists.
- Do not draw a group WebSocket node; no group route/consumer exists.
- Do not draw an email-verification flow; no endpoint/writer exists.
- Do not draw a scheduled publisher job; none was found.
- Do not show direct file URLs as authorized by the privacy layer; media access control is not implemented in source.

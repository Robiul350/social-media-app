# API Analysis

Conventions:

- Base URL: `/api/`. The SPA defaults to `http://127.0.0.1:8000/api/` and overrides it with `VITE_API_BASE_URL`.
- Default DRF authentication is JWT (`JWTAuthentication`). The global default permission is `IsAuthenticatedOrReadOnly`, but every local REST view declares its own permission class, so anonymous read-only REST access is not available in practice.
- HTTP access tokens are sent as `Authorization: Bearer <access>`. WebSocket tokens are passed as `?token=<access>`.
- No ViewSets and no `@action` decorators exist in the audited backend. All endpoints are `APIView`, DRF `generics.*APIView`, or SimpleJWT views.
- DRF automatically supports `HEAD`/`OPTIONS`; only meaningful verbs are listed.
- Status column uses the vocabulary defined in `CLAUDE_MASTER_PROMPT.md`.
- Response shapes below are source-derived. Paginated feed responses depend on the presence of `?page=`.

---

## 1. Root, admin, and media

| ID | URL | Method | Auth | Response / notes | Status |
| --- | --- | --- | --- | --- | --- |
| API-001 | `/` | GET | None | JSON health response from `config/urls.py`: message, `"project": "Social Media App"`, `"version": "1.0"`, status `Running`. | Implemented |
| API-002 | `/admin/` | GET/POST | Django staff/superuser/model permissions | Custom SocialConnect admin dashboard, analytics, roles, system pages, and model changelists. | Implemented |
| API-003 | `/media/<path>` | GET | None at Django level | Uploaded media; served only when `DJANGO_DEBUG=True` in source. Production strategy is `[NOT VERIFIED - USER CONFIRMATION REQUIRED]`. | Implemented (dev only) |

`backend/config/views.py` contains an unused `home()` view with a different health payload. It is not routed.

---

## 2. Users API — `/api/users/`

| ID | Endpoint | Method | Payload / query | Response / notes | Status |
| --- | --- | --- | --- | --- | --- |
| API-010 | `register/` | POST | `username`, `email`, `password`, `password2` | `201 {"message":"Registration successful.","user":{id,username,email}}`; password validation; profile auto-created by signal. | Implemented |
| API-011 | `login/` | POST | `username`, `password` | `200 {"message":"Login successful.","user":{...},"tokens":{refresh,access}}`; username-only; inactive users rejected. | Implemented |
| API-012 | `token/refresh/` | POST | `refresh` | `200 {access,refresh}`; rotating refresh; old refresh blacklisted. | Implemented |
| API-013 | `logout/` | POST | `refresh` | `200 {"detail":"Logout successful."}`; blacklists supplied refresh token. | Implemented |
| API-014 | `password/change/` | POST | `current_password`, `new_password` | `200 {"detail":"Password changed successfully."}`; revokes all outstanding refresh tokens. | Implemented (backend only in SPA) |
| API-015 | `password/reset/` | POST | `email` | Generic `200` response; emailed link only; no token in JSON. Email delivery is environment-dependent. | Implemented / Needs Verification |
| API-016 | `password/reset/confirm/` | POST | `uid`, `token`, `password` | `200 {"detail":"Password reset successfully."}`; revokes refresh tokens. No SPA confirm route found. | Implemented / Partial |
| API-017 | `account/deactivate/` | POST | — | `200 {"detail":"Account deactivated."}`; sets `is_active=False` and revokes refresh tokens. | Implemented (backend only in SPA) |
| API-018 | `profile/` | GET | — | `{id,username,first_name,last_name,email,profile:{...}}`. | Implemented |
| API-019 | `profile/` | PATCH | Profile fields plus `first_name`, `last_name`; optional `profile_picture`, `cover_photo`, `remove_profile_picture`, `remove_cover_photo` | `200 {"message":"Profile updated successfully.",...}`; avatar ≤5 MB, cover ≤10 MB; `is_verified` read-only. | Implemented |
| API-020 | `search/` | GET | `?suggested=true` or `?search=`/`?q=` | Array of `PublicProfileSerializer`; suggested excludes self, blocked, followed; general search limited to 50. | Implemented |
| API-021 | `stories/` | GET | — | Array of visible stories; privacy, expiry, private-profile, and block rules applied. | Implemented |
| API-022 | `stories/` | POST | `media`, `text`, `privacy` | `201 StorySerializer`; server sets author and 24-hour expiry; media ≤25 MB. | Implemented |
| API-023 | `stories/<pk>/view/` | POST | — | `200 {"viewed":true}`; 404 if not visible. | Implemented |
| API-024 | `stories/<pk>/react/` | POST | `reaction_type` | `201`/`200 StoryReactionSerializer`; seven reaction types; notification emitted on every POST including updates. | Partial |
| API-025 | `stories/<pk>/react/` | DELETE | — | `204` with a body (non-standard). | Partial |
| API-026 | `stories/<pk>/reactions/` | GET | — | `{story_id,total_reactions,counts_by_type,user_reaction,reactions:[...]}`; story must be visible. | Implemented (backend only in SPA) |
| API-027 | `<user_id>/posts/` | GET | — | Array of visible posts; private/blocked authors return `[]`; no pagination. | Implemented |
| API-028 | `<pk>/` | GET | — | `PublicProfileSerializer`; blocked users 404; private profile hides details and sets `can_view_profile:false`. | Implemented |

Missing: story edit/delete, email verification endpoint, self-service verification.

---

## 3. Posts API — `/api/posts/`

| ID | Endpoint | Method | Payload / query | Response / notes | Status |
| --- | --- | --- | --- | --- | --- |
| API-030 | `` | GET | `?bookmarked=true`, `?drafts=true` | Array of `PostSerializer`. Default shows visible, non-draft, published or due scheduled posts. `drafts=true` returns **all** caller-authored posts (contract bug). | Implemented / Partial |
| API-031 | `` | POST | `content`, `image`, `video`, `audience`, `is_draft`, `is_pinned`, `scheduled_for` | `201 PostSerializer`; content or media required; image ≤10 MB, video ≤100 MB; `#hashtags` synced. | Implemented |
| API-032 | `<pk>/` | GET/PUT/PATCH/DELETE | Partial post fields for writes | `200`/`204`; visible posts plus own drafts; writes author-only. | Implemented |
| API-033 | `<pk>/bookmark/` | POST | — | `201 {"bookmarked":true}` / `200 {"bookmarked":false}`; visible non-draft post required. | Implemented |
| API-034 | `<pk>/pin/` | POST | — | `200 {"pinned":bool}`; author only; no feed ordering consumes the flag. | Partial |
| API-035 | `<pk>/repost/` | POST | — | `201`/`200 PostSerializer`; own post rejected; idempotent per author+source; no notification. | Partial |
| API-036 | `<pk>/poll/<option_id>/vote/` | POST | — | `200 {"voted":true,"option_id":id}`; one active vote per poll enforced in view with `select_for_update`; DB uniqueness is per option. | Partial |
| API-037 | `<pk>/report/` | POST | `reason` | `201 {"reported":true,"report_id":id}`; create-only; no status/moderation endpoint. | Partial |

Missing: poll CRUD/list, hashtag endpoints, multi-image upload through `PostImage`, scheduled publisher job.

---

## 4. Social API — `/api/social/`

| ID | Endpoint | Method | Payload / query | Response / notes | Status |
| --- | --- | --- | --- | --- | --- |
| API-040 | `feed/` | GET | `page`, `page_size` | Bare array when no `page`; `{count,next,previous,results}` when `page` present. Page size 10 default, max 50. | Implemented |
| API-041 | `posts/<post_id>/like/` | POST | — | `201`/`200 {message,liked,like_count}`; creates notification. | Implemented |
| API-042 | `posts/<post_id>/comments/` | GET | — | Array of `CommentSerializer`; visible post; blocked users excluded; no pagination. | Implemented |
| API-043 | `posts/<post_id>/comments/` | POST | `content`, optional `parent` | `201 CommentSerializer`; parent same-post validation; mentions and comment/reply notifications. | Implemented |
| API-044 | `comments/<pk>/react/` | POST | `reaction` | `200 {reacted,...}`; toggle/update; no notification. | Partial |
| API-045 | `comments/<pk>/` | GET/PUT/PATCH/DELETE | `content` for writes | `200`/`204`; owner-only writes; visibility/block filtering. | Implemented |
| API-046 | `users/<user_id>/follow/` | POST | — | `201 {message}` / `200 {message,following:true}`; creates follow notification. | Implemented |
| API-047 | `users/<user_id>/follow/` | DELETE | — | `200`/`404`. | Implemented |
| API-048 | `users/<user_id>/friend-request/` | POST | — | `201`/`200 FriendRequestSerializer` or `409`; self/block guards; reverse-pending and already-friends conflicts. | Implemented |
| API-049 | `friend-requests/` | GET | `?direction=incoming|outgoing` | Array of pending requests; default incoming; invalid direction 400. | Implemented |
| API-050 | `friend-requests/<pk>/accept/` | POST | — | `200 {id,status:"accepted"}`; receiver only; no notification to sender. | Partial |
| API-051 | `friend-requests/<pk>/reject/` | POST | — | `200 {id,status:"rejected"}`; receiver only; no notification. | Partial |
| API-052 | `friend-requests/<pk>/` | DELETE | — | `204`/`404`; sender cancels pending request. | Implemented |
| API-053 | `friends/` | GET | — | Array of `UserSummarySerializer`; accepted friends minus blocked. | Implemented |
| API-054 | `friends/<user_id>/` | DELETE | — | `204`/`404`. | Implemented |
| API-055 | `users/<user_id>/mutual-friends/` | GET | — | Array of users; block-aware intersection. | Implemented (backend only in SPA) |
| API-056 | `users/following/` | GET | — | Array of users; excludes blocked. | Implemented |
| API-057 | `users/followers/` | GET | — | Array of users; excludes blocked. | Implemented |
| API-058 | `blocks/` | GET | — | Caller's block list. | Implemented (backend only in SPA) |
| API-059 | `users/<user_id>/block/` | POST | — | `201`/`200 {"blocked":true}`; immediately changes visibility/chat/notifications; history retained. | Implemented |
| API-060 | `users/<user_id>/block/` | DELETE | — | `204`/`404`. | Implemented |

---

## 5. Notifications API — `/api/notifications/`

| ID | Endpoint | Method | Payload | Response / notes | Status |
| --- | --- | --- | --- | --- | --- |
| API-070 | `` | GET | — | Recipient-only array, newest first; `post`/`comment` IDs masked to `null` when no longer visible. | Implemented |
| API-071 | `<pk>/read/` | PATCH | — | `200 {"message":"Notification marked as read."}`; recipient-only; no WebSocket update emitted. | Partial |
| API-072 | `read-all/` | POST | — | `200 {"message":...,"updated_count":n}`. | Implemented |
| API-073 | `unread-count/` | GET | — | `200 {"unread_count":n}`; used by navbar polling. | Implemented |
| API-074 | `preferences/` | GET | — | Eight booleans: `likes`, `comments`, `replies`, `follows`, `friend_requests`, `messages`, `mentions`, `story_reactions`. | Implemented |
| API-075 | `preferences/` | PATCH | Any subset of the eight booleans | Updated preference object; invalid key 400. | Implemented |

Creation pipeline: `notifications.utils.create_notification` skips self/blocked recipients, honours preferences, persists the record, and publishes on commit to `notifications_<recipient_id>`.

---

## 6. Chat API — `/api/chat/`

| ID | Endpoint | Method | Payload | Response / notes | Status |
| --- | --- | --- | --- | --- | --- |
| API-080 | `conversations/` | GET | — | Array of `{id,username,first_name,last_name,profile_picture,last_message,last_message_at,unread_count}`; direct messages only; blocked pairs excluded; no pagination. | Implemented |
| API-081 | `conversations/<user_id>/` | GET | — | Array of `MessageSerializer`; both directions; soft-deleted excluded. | Implemented |
| API-082 | `conversations/<user_id>/` | POST | `content`, optional `attachment` | `201 MessageSerializer`; allowed MIME prefixes; ≤25 MB; creates notification and WS broadcast. | Implemented |
| API-083 | `conversations/<user_id>/read/` | POST | — | `200 {message,updated_count}`; broadcasts read receipt with message IDs. | Implemented |
| API-084 | `unread-count/` | GET | — | `200 {"unread_count":n}`; excludes blocked senders and soft-deleted messages. | Implemented |
| API-085 | `messages/<pk>/` | PATCH | `content` | `200 MessageSerializer`; sender only; sets `edited_at`; broadcasts update for direct messages. | Partial |
| API-086 | `messages/<pk>/` | DELETE | — | `204`; soft delete; broadcasts deletion for direct messages. | Implemented |
| API-087 | `groups/` | GET | — | Array of `GroupConversationSerializer`; groups where caller has membership. | Implemented (backend only in SPA) |
| API-088 | `groups/` | POST | `name`, `avatar`, `member_ids` | `201 GroupConversationSerializer`; creator is admin, others members; max 50 others; all must be chat-eligible. | Partial |
| API-089 | `groups/<group_id>/messages/` | GET/POST | `content`, optional `attachment` for POST | Array / `201 MessageSerializer`; member-only; no WebSocket broadcast. | Partial |

Missing: group WebSocket route, group membership management endpoints (add/remove/role/mute/archive), hard delete.

---

## 7. WebSocket API

### API-090 — `/ws/chat/<user_id>/?token=<access>`

Authentication: query-string access token validated by `chat.middleware.JWTAuthMiddleware`; only active users accepted.

| Close code / event | Meaning |
| --- | --- |
| `4401` | Missing/invalid token or inactive user. |
| `4400` | Target user is the caller. |
| `4404` | Target user does not exist. |
| `4403` | Chat disallowed by block/message/privacy rules. |
| `{"type":"typing","is_typing":bool}` | Client → server; broadcasts `{"type":"typing","user_id","is_typing"}`. |
| `{"message":"..."}` / `{"type":"message","message":"..."}` | Client → server; permission recheck, persist, notify, broadcast. Text is trimmed, must be non-empty, and is limited to 5000 characters in `chat/consumers.py`. |
| `{"type":"chat_message",...}` | Server → client; persisted message payload including `id`, `sender_id`, `receiver_id`, `created_at`, and `is_read`. Consumer-originated frames include `sender_username`; REST-originated frames omit it. |
| `{"error":"..."}` | Server → client for invalid/blank/too-long/non-text messages. |
| `{"type":"presence","user_id":...,"is_online":bool}` | Online/offline broadcast on connect/disconnect. |
| `{"type":"typing","user_id":...,"is_typing":bool}` | Typing broadcast. |
| `{"type":"read_receipt","reader_id":...,"message_ids":[...]}` | Broadcast after REST read action. |
| `{"type":"message_updated","message_id":...,"content":...,"edited_at":...}` | REST-originated direct-message edit. |
| `{"type":"message_deleted","message_id":...,"deleted_at":...}` | REST-originated direct-message soft delete. |

Outbound `chat_message` from the consumer includes `sender_username`; the REST POST broadcast omits it. Clients should treat `sender_username` as optional.

### API-091 — `/ws/notifications/?token=<access>`

- Closes `4401` for anonymous/invalid users.
- On accept, joins `notifications_<user_id>`.
- Receives `{"type":"notification","notification":{id,sender,sender_username,notification_type,post,comment,is_read,created_at}}`.
- Client messages are ignored.
- The channel-layer event emitted by `create_notification()` is `notification.created`; `NotificationConsumer` translates it to the client frame `{"type":"notification","notification":...}`.
- Read actions do not push updates; clients refresh counts locally.

---

## 8. Pagination and filtering

- Feed: pagination only when `?page=` is present; `page_size` alone does not paginate.
- Search, stories, comments, notifications, bookmarks, connections, friend requests, user posts, chat history, group lists, and admin lists have no REST pagination in the SPA consumption path; admin model changelists use Django pagination.
- The SPA compensates with IntersectionObserver only on the home feed; other pages render the first response only.
- Privacy and block filtering are applied through `social/access.py` and view-level checks, not database row-level security.

---

## 9. API-to-SPA coverage

Fully covered by SPA: auth/profile, stories list/create/view, feed, post CRUD, likes/comments/bookmarks, reposts/pins/reports, follow/friend/block, connections, search, direct messages, notifications, preferences.

Backend-only or partial in SPA: poll voting, story reactions/list, comment reactions, mutual friends, block list management, group conversations, message edit/delete triggers, password change/reset/deactivate screens, hashtag browsing (no endpoint), moderation/status workflow, multi-image upload, scheduled publishing controls, admin analytics (Django admin instead of SPA).

---

## 10. Security notes for technical documentation

- JWT access tokens are stored in browser `localStorage`; WebSocket tokens appear in the query string. Both are XSS/log-leak risks that must be reported as risks, not silently accepted.
- Route guards check token presence only; validity is enforced by API authentication and the Axios refresh flow.
- Authorization is enforced per view/serializer plus `social/access.py`; object ownership checks are application-level.
- Media URLs are not authorization-aware; direct file URLs bypass application privacy filters. Production media strategy is `[NOT VERIFIED - USER CONFIRMATION REQUIRED]`.
- `MessageSerializer` includes `edited_at` and `deleted_at` but does not declare them read-only; client-supplied values may be accepted on REST create/update. Treat this as a verified source-level risk.
- No rate-limiting configuration was verified in source. `[NOT VERIFIED - USER CONFIRMATION REQUIRED]`

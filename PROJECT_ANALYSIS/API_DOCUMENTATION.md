# API Documentation

## Conventions

- Base URL: `/api/`. The SPA defaults to `http://127.0.0.1:8000/api/` and overrides it with `VITE_API_BASE_URL`.
- Default DRF authentication: JWT (`JWTAuthentication`). Default permission: `IsAuthenticatedOrReadOnly`; most private endpoints explicitly require `IsAuthenticated`.
- Access tokens are sent as `Authorization: Bearer <access>`. WebSocket tokens are passed as `?token=<access>`.
- SimpleJWT access lifetime defaults to 30 minutes, refresh lifetime to 7 days; refresh rotation and blacklisting are enabled.
- Status markers: **[I]** implemented, **[P]** partial, **[M]** missing/no endpoint.
- DRF also accepts `HEAD`/`OPTIONS` automatically; only meaningful verbs are listed.
- Response shapes below reflect source code; paginated feed responses depend on the presence of `?page=`.

## Root and admin

| URL | Method | Auth | Response / notes | Status |
| --- | --- | --- | --- | --- |
| `/` | GET | None | `200 {"message":"Social Media API is running successfully!","project":"Social Media App","status":"Running","version":"1.0"}`; view defined inline in `config/urls.py`. | [I] |
| `/admin/` | GET/POST | Django staff/superuser/model permissions | Custom SocialConnect admin dashboard, analytics, roles, system pages, model changelists. | [I] |
| `/media/<path>` | GET | None | Uploaded media; served only when `DJANGO_DEBUG=True` via `static()`. | [I] dev only |

A second, unused `home()` exists in `backend/config/views.py` with a different response shape; it is not routed.

## Users API — `/api/users/`

| Endpoint | Method | Payload / query | Response | Notes | Status |
| --- | --- | --- | --- | --- | --- |
| `register/` | POST | `username`, `email`, `password`, `password2` | `201 {"message":"Registration successful.","user":{id,username,email}}` | Password validated by `validate_password`; profile auto-created by signal. | [I] |
| `login/` | POST | `username`, `password` | `200 {"message":"Login successful.","user":{...},"tokens":{refresh,access}}` | Username-only; inactive users rejected. | [I] |
| `token/refresh/` | POST | `refresh` | `200 {access,refresh}` | Rotating refresh; old token blacklisted. | [I] |
| `logout/` | POST | `refresh` | `200 {"detail":"Logout successful."}` | Blacklists supplied refresh only. | [I] |
| `password/change/` | POST | `current_password`, `new_password` | `200 {"detail":"Password changed successfully."}` | Revokes all outstanding refresh tokens. | [I] |
| `password/reset/` | POST | `email` | `200 {"detail":"If the account exists, password reset instructions were sent."}` | Generic response; emailed link only; no token in JSON. | [I] |
| `password/reset/confirm/` | POST | `uid`, `token`, `password` | `200 {"detail":"Password reset successfully."}` | Revokes refresh tokens. | [I] |
| `account/deactivate/` | POST | — | `200 {"detail":"Account deactivated."}` | Sets `is_active=False`, revokes refresh tokens. | [I] |
| `profile/` | GET | — | `{id,username,first_name,last_name,email,profile:{...}}` | Profile includes all `ProfileSerializer` fields; write-only removal flags not echoed. | [I] |
| `profile/` | PATCH | Profile fields plus `first_name`, `last_name`; optional `profile_picture`, `cover_photo`, `remove_profile_picture`, `remove_cover_photo` | `200 {"message":"Profile updated successfully.",...}` | Avatar ≤5 MB image; cover ≤10 MB image; `is_verified` read-only. | [I] |
| `search/` | GET | `?suggested=true` or `?search=`/`?q=` | Array of `PublicProfileSerializer` | Suggested excludes self, blocked, followed; general search limited to 50. | [I] |
| `stories/` | GET | — | Array of visible `StorySerializer` objects | Privacy, expiry, private profile, and block rules applied. | [I] |
| `stories/` | POST | `media`, `text`, `privacy` | `201 StorySerializer` | Server sets author and 24-hour expiry; media ≤25 MB. | [I] |
| `stories/<pk>/view/` | POST | — | `200 {"viewed":true}` | 404 if story not visible. | [I] |
| `stories/<pk>/react/` | POST | `reaction_type` | `201`/`200 StoryReactionSerializer` | Seven reaction types; creates notification on every POST, including updates. | [I] |
| `stories/<pk>/react/` | DELETE | — | `204` with a body (non-standard) | Removes reaction. | [I] |
| `stories/<pk>/reactions/` | GET | — | `{story_id,total_reactions,counts_by_type,user_reaction,reactions:[...]}` | Story must be visible. | [I] |
| `<user_id>/posts/` | GET | — | Array of visible posts | Private/blocked authors return `[]`; no pagination. | [I] |
| `<pk>/` | GET | — | `PublicProfileSerializer` | Blocked users 404; private profile hides `profile` and sets `can_view_profile:false`. | [I] |

Missing: story edit/delete, email verification, self-service verification.

## Posts API — `/api/posts/`

| Endpoint | Method | Payload / query | Response | Notes | Status |
| --- | --- | --- | --- | --- | --- |
| `` | GET | `?bookmarked=true`, `?drafts=true` | Array of `PostSerializer` | Default: visible, non-draft, published or scheduled-due. `drafts=true` returns **all** caller-authored posts. | [I] with contract bug |
| `` | POST | `content`, `image`, `video`, `audience`, `is_draft`, `is_pinned`, `scheduled_for` | `201 PostSerializer` | Content or media required; image ≤10 MB, video ≤100 MB; `#hashtags` synced. | [I] |
| `<pk>/` | GET/PUT/PATCH/DELETE | Partial post fields for writes | `200`/`204` | Visible posts plus own drafts; writes author-only. | [I] |
| `<pk>/bookmark/` | POST | — | `201 {"bookmarked":true}` / `200 {"bookmarked":false}` | Visible non-draft post required. | [I] |
| `<pk>/pin/` | POST | — | `200 {"pinned":bool}` | Author only; no feed ordering consumes the flag. | [P] |
| `<pk>/repost/` | POST | — | `201`/`200 PostSerializer` | Own post rejected; idempotent per author+source. No notification. | [P] |
| `<pk>/poll/<option_id>/vote/` | POST | — | `200 {"voted":true,"option_id":id}` | One active vote per poll enforced in view; DB uniqueness only per option. | [P] |
| `<pk>/report/` | POST | `reason` | `201 {"reported":true,"report_id":id}` | Create-only; no status/moderation endpoint. | [P] |

Missing: poll CRUD/list, hashtag endpoints, multi-image upload via `PostImage`, scheduled publisher job.

## Social API — `/api/social/`

| Endpoint | Method | Payload / query | Response | Notes | Status |
| --- | --- | --- | --- | --- | --- |
| `feed/` | GET | `page`, `page_size` | Bare array when no `page`; `{count,next,previous,results}` when `page` present | Page size 10 default, max 50; pagination is opt-in only via `page`. | [I] |
| `posts/<post_id>/like/` | POST | — | `201`/`200 {message,liked,like_count}` | Creates like notification. | [I] |
| `posts/<post_id>/comments/` | GET | — | Array of `CommentSerializer` | Visible post; blocked users excluded; no pagination. | [I] |
| `posts/<post_id>/comments/` | POST | `content`, `parent` | `201 CommentSerializer` | Parent same-post validation; mentions + comment/reply notifications. | [I] |
| `comments/<pk>/react/` | POST | `reaction` | `200 {reacted,...}` | Toggle/update; no notification. | [P] |
| `comments/<pk>/` | GET/PUT/PATCH/DELETE | `content` for writes | `200`/`204` | Owner-only writes; visible-post/block filtering. | [I] |
| `users/<user_id>/follow/` | POST | — | `201 {message}` / `200 {message,following:true}` | Creates follow notification. | [I] |
| `users/<user_id>/follow/` | DELETE | — | `200`/`404` | Unfollow. | [I] |
| `users/<user_id>/friend-request/` | POST | — | `201`/`200 FriendRequestSerializer` or `409` | Self/block guards; reverse-pending and already-friends conflicts. | [I] |
| `friend-requests/` | GET | `?direction=incoming|outgoing` | Array of pending requests | Default incoming; invalid direction 400. | [I] |
| `friend-requests/<pk>/accept/` | POST | — | `200 {id,status:"accepted"}` | Receiver only; no notification to sender. | [P] |
| `friend-requests/<pk>/reject/` | POST | — | `200 {id,status:"rejected"}` | Receiver only; no notification. | [P] |
| `friend-requests/<pk>/` | DELETE | — | `204`/`404` | Sender cancels pending request. | [I] |
| `friends/` | GET | — | Array of `UserSummarySerializer` | Accepted friends minus blocked. | [I] |
| `friends/<user_id>/` | DELETE | — | `204`/`404` | Unfriend. | [I] |
| `users/<user_id>/mutual-friends/` | GET | — | Array of users | Block-aware intersection. | [I] |
| `users/following/` | GET | — | Array of users | Excludes blocked; no explicit ordering. | [I] |
| `users/followers/` | GET | — | Array of users | Excludes blocked. | [I] |
| `blocks/` | GET | — | Array of users | Caller's block list. | [I] |
| `users/<user_id>/block/` | POST | — | `201`/`200 {"blocked":true}` | Immediately changes visibility/chat/notifications; history retained. | [I] |
| `users/<user_id>/block/` | DELETE | — | `204`/`404` | Unblock. | [I] |

## Notifications API — `/api/notifications/`

| Endpoint | Method | Payload | Response | Notes | Status |
| --- | --- | --- | --- | --- | --- |
| `` | GET | — | Array of `NotificationSerializer` | Recipient-only; newest first; `post`/`comment` IDs masked to `null` if no longer visible. | [I] |
| `<pk>/read/` | PATCH | — | `200 {"message":"Notification marked as read."}` | Recipient-only; no WebSocket update emitted. | [P] |
| `read-all/` | POST | — | `200 {"message":...,"updated_count":n}` | Marks all recipient notifications read. | [I] |
| `unread-count/` | GET | — | `200 {"unread_count":n}` | Used by navbar polling. | [I] |
| `preferences/` | GET | — | Eight booleans | `likes, comments, replies, follows, friend_requests, messages, mentions, story_reactions`. | [I] |
| `preferences/` | PATCH | Any subset of the eight booleans | Updated preference object | Partial update; invalid key 400. | [I] |

Creation pipeline: `notifications.utils.create_notification` skips self/blocked recipients, honours preferences, persists the record, and publishes on commit to `notifications_<recipient_id>`.

## Chat API — `/api/chat/`

| Endpoint | Method | Payload | Response | Notes | Status |
| --- | --- | --- | --- | --- | --- |
| `conversations/` | GET | — | Array of `{id,username,first_name,last_name,profile_picture,last_message,last_message_at,unread_count}` | Direct messages only; blocked pairs excluded; no pagination. | [I] |
| `conversations/<user_id>/` | GET | — | Array of `MessageSerializer` | Both directions; soft-deleted excluded. | [I] |
| `conversations/<user_id>/` | POST | `content`, optional `attachment` | `201 MessageSerializer` | Allowed MIME prefixes; ≤25 MB; creates notification and WS broadcast. | [I] |
| `conversations/<user_id>/read/` | POST | — | `200 {message,updated_count}` | Broadcasts read receipt with message IDs. | [I] |
| `unread-count/` | GET | — | `200 {"unread_count":n}` | Excludes blocked senders and soft-deleted messages. | [I] |
| `messages/<pk>/` | PATCH | `content` | `200 MessageSerializer` | Sender only; sets `edited_at`; broadcasts update for direct messages. | [P] |
| `messages/<pk>/` | DELETE | — | `204` | Soft delete; broadcasts deletion for direct messages. | [I] |
| `groups/` | GET | — | Array of `GroupConversationSerializer` | Groups where caller has membership. | [I] |
| `groups/` | POST | `name`, `avatar`, `member_ids` | `201 GroupConversationSerializer` | Creator admin, others member; max 50 others; all must be chat-eligible. | [P] |
| `groups/<group_id>/messages/` | GET/POST | `content`, optional `attachment` for POST | Array / `201 MessageSerializer` | Member-only; no WebSocket broadcast. | [P] |

Missing: group WebSocket route, group membership management (add/remove/role/mute/archive), hard delete.

## WebSocket API

### `/ws/chat/<user_id>/?token=<access>`

Authentication: query-string access token validated by `chat.middleware.JWTAuthMiddleware`; only active users accepted.

| Close code / event | Meaning |
| --- | --- |
| `4401` | Missing/invalid token or inactive user. |
| `4400` | Target user is the caller. |
| `4404` | Target user does not exist. |
| `4403` | Chat disallowed by block/message/privacy rules. |
| `{"type":"typing","is_typing":bool}` | Client → server; broadcasts `{"type":"typing","user_id","is_typing"}`. |
| `{"message":"text"}` | Client → server; rechecks permission, persists, notifies, broadcasts `chat_message`. |
| `{"error":"..."}` | Server → client for invalid/blank/too-long/non-text messages. |
| `presence_update` / `presence` | Online/offline broadcast. |
| `typing_update` / `typing` | Typing broadcast. |
| `read_receipt` | Reader ID plus message IDs after REST read action. |
| `message_updated`, `message_deleted` | REST-originated direct-message events. |

Outbound `chat_message` from the consumer includes `sender_username`; the REST POST broadcast omits it — clients should treat it as optional.

### `/ws/notifications/?token=<access>`

- Closes `4401` for anonymous/invalid users.
- On accept, joins `notifications_<user_id>`.
- Receives `{"type":"notification","notification":{id,sender,sender_username,notification_type,post,comment,is_read,created_at}}`.
- Client messages are ignored.
- Read actions do not push updates; clients refresh counts locally.

## Pagination and filtering summary

- Feed: pagination only when `page` is present; `page_size` alone does not paginate.
- Search, stories, comments, notifications, bookmarks, connections, friend requests, user posts, chat history, and group lists have **no pagination** in the REST API.
- The SPA compensates with IntersectionObserver only on the home feed; other pages render the first response only.

## API-to-SPA coverage

Fully covered by SPA: auth/profile, stories list/create/view, feed, post CRUD, likes/comments/bookmarks/reposts/pins/reports, follow/friend/block, connections, search, messages (direct), notifications, preferences.

Backend-only or partial in SPA: poll voting, story reactions, story reaction list, comment reactions, mutual friends, block list management, group conversations, message edit/delete actions, password change/reset/deactivate screens, hashtag endpoints (none), moderation/status workflow, multi-image upload, scheduled publishing controls.

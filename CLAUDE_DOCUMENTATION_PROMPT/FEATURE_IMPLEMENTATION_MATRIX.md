# Feature Implementation Matrix

Status vocabulary matches `CLAUDE_MASTER_PROMPT.md`:

- **Implemented** — backend logic and a reachable UI/API path are present with no known blocking gap in the primary flow.
- **Partial** — code exists, but part of the end-to-end flow, UI, notification, ordering, validation, or lifecycle is incomplete.
- **Backend only** — REST/WebSocket/model capability exists in Django; no corresponding SPA screen or action was found.
- **Planned / documented** — mentioned in historical docs or field intent but not proven in active source.
- **Not Found** — no supporting route, model, endpoint, component, test, or job was found.
- **Needs Verification** — runtime, environment, deployment, or owner confirmation is required; use `[NOT VERIFIED - USER CONFIRMATION REQUIRED]`.

This matrix is source-oriented. Historical reports were used only to locate candidate features and contradictions, never as proof of current status.

---

## 1. Executive summary

| Domain | Overall status | Main caveat |
| --- | --- | --- |
| Identity and access | Implemented with caveats | Username-only login; JWTs in `localStorage`; route guard checks token presence only. |
| Password lifecycle | Partial / backend only | REST endpoints exist; no dedicated SPA reset/confirm/deactivate screens. |
| Profiles and discovery | Implemented with caveats | Active screen is `UserProfile.jsx`; legacy `Profile.jsx` is unrouted. |
| Posts and feed | Implemented core, several partial extensions | Draft filter contract, pin ordering, scheduling, multi-image upload, polls, reports remain partial/backend-only; no draft/scheduling UI found. |
| Social graph | Implemented core | Block-list management and mutual-friend UI are backend-only; accept/reject notifications absent. |
| Stories | Partial | List/create/view UI exists; reaction UI, edit/delete, and viewed-state persistence are missing. |
| Notifications | Implemented with caveats | REST + WebSocket + preferences UI; read actions do not emit live updates; no pagination. |
| Direct messaging | Implemented with caveats | REST + WebSocket UI; attachment-only sends and message edit/delete controls are missing. |
| Group messaging | Backend only / partial | REST models/endpoints exist; no group UI or group WebSocket. |
| Custom admin | Implemented with caveats | Real-data dashboard/analytics/roles/system pages; moderation workflow absent; browser smoke result unverified. |
| PWA | Partial | App-shell caching only; no offline data, push notifications, install flow, or full icon set. |
| Frontend tests | Not Found | Vitest/jsdom installed but no test files or script. |
| Production deployment | Needs Verification / Not Found | Settings support exists; topology, proxy, static/media hosting, Redis runtime, and CI/CD are unverified. |

---

## 2. Identity, access, and account lifecycle

| ID | Feature | Backend evidence | SPA / admin evidence | Status | Gap / caveat |
| --- | --- | --- | --- | --- | --- |
| F-001 | Registration | `POST /api/users/register/` via `RegisterSerializer`; password validation; profile auto-created by `users/signals.py` | `frontend/src/pages/Register.jsx` posts username/email/password/password2 and redirects to login | Implemented | Form labels are not programmatically associated; error container lacks `role="alert"`. |
| F-002 | Login | `POST /api/users/login/` returns user + SimpleJWT tokens; inactive users rejected | `Login.jsx` persists `access`, `refresh`, `user_id`, `username` | Implemented | Username-only despite email field; generic catch swallows explicit invalid-response message. |
| F-003 | JWT refresh | `POST /api/users/token/refresh/`; rotation and blacklisting | `frontend/src/api/axios.js` refreshes once on 401, replays request, shares concurrent refresh | Implemented | Route guard checks token presence only, not validity. |
| F-004 | Logout | `POST /api/users/logout/` blacklists supplied refresh token | Navbar/AppShell logout clears localStorage and dispatches auth-change | Implemented | Endpoint-level test coverage requires inspection; token remains readable by page JS until cleared. |
| F-005 | Change password | `POST /api/users/password/change/`; revokes outstanding refresh tokens | No dedicated SPA screen found | Backend only | `[NOT VERIFIED - USER CONFIRMATION REQUIRED]` whether UI is required. |
| F-006 | Request password reset | `POST /api/users/password/reset/`; generic response; email link only | No `/forgot-password` route found | Backend only / Partial | Email backend configuration and delivery are `[NOT VERIFIED - USER CONFIRMATION REQUIRED]`. |
| F-007 | Confirm password reset | `POST /api/users/password/reset/confirm/`; revokes refresh tokens | No reset-confirm SPA route found | Backend only / Partial | Emailed link points to an unrouted frontend path. |
| F-008 | Deactivate account | `POST /api/users/account/deactivate/`; sets `is_active=False`, revokes tokens | No SPA screen found | Backend only | `[NOT VERIFIED - USER CONFIRMATION REQUIRED]` whether self-service deactivation is in scope. |
| F-009 | Email verification flag | `User.email_verified` field exists | No UI; no writer/endpoint found | Not Found | Field intent is `[NOT VERIFIED - USER CONFIRMATION REQUIRED]`. |
| F-010 | Protected SPA routes | Presence check on `localStorage.access`; fallback redirect | `App.jsx` router guards | Implemented | Presence-only guard; expired token is handled by API refresh/clear flow. |

## 3. Profiles and discovery

| ID | Feature | Backend evidence | SPA / admin evidence | Status | Gap / caveat |
| --- | --- | --- | --- | --- | --- |
| F-011 | Own profile read/update | `GET/PATCH /api/users/profile/`; profile serializer; image upload/removal; privacy fields | `EditProfile.jsx`; profile store in navbar/AppShell | Implemented | No retry on load failure; invalid file selection does not disable submit. |
| F-012 | Public profile | `GET /api/users/<pk>/`; masked private profile; block check; relationship flags | `UserProfile.jsx` active; renders stats, media, actions, posts | Implemented | `Profile.jsx` is unrouted legacy duplicate. |
| F-013 | Profile privacy settings | `is_private`, `allow_comments`, `allow_messages` fields and serializer writes | `EditProfile.jsx` exposes switches/selects | Implemented | No dedicated `/settings` route. |
| F-014 | Profile picture/cover upload | Multipart `PATCH`; avatar ≤5 MB, cover ≤10 MB | Previews, validation, removal controls in `EditProfile.jsx` | Implemented | Production media authorization is `[NOT VERIFIED - USER CONFIRMATION REQUIRED]`. |
| F-015 | User search | `GET /api/users/search/?search=`/`?q=` | `UserSearch.jsx`, navbar/sidebar/right-rail search | Implemented | Render-phase URL state sync; abort/cache-ref path can leave loading stuck. |
| F-016 | Suggested accounts | `?suggested=true`, up to five non-followed accounts | Right rail and search UI | Implemented | Suggestions exclude self, blocked, and followed users. |
| F-017 | Mutual friends | `GET /api/social/users/<id>/mutual-friends/` | No dedicated UI found | Backend only | `[NOT VERIFIED - USER CONFIRMATION REQUIRED]` whether display is required. |
| F-018 | Block list management | `GET /api/social/blocks/` | No dedicated block-list screen; unblock action on public profile | Backend only / Partial | Block/unblock flow from profile is implemented; list screen is absent. |

## 4. Posts, content, and feed

| ID | Feature | Backend evidence | SPA / admin evidence | Status | Gap / caveat |
| --- | --- | --- | --- | --- | --- |
| F-019 | Post CRUD | `GET/POST /api/posts/`, `GET/PUT/PATCH/DELETE /api/posts/<pk>/`; author-only writes | Home composer, edit/delete menu, post detail, profile posts | Implemented | Content-or-media validation is serializer-level, not a DB constraint. |
| F-020 | Feed | `GET /api/social/feed/`; visibility/block filtering; optional pagination with `?page=` | `home.jsx` loads `?page=1` and uses IntersectionObserver | Implemented | Pagination is opt-in only; `page_size` alone does not paginate. |
| F-021 | Audience control | `Post.audience` `public/followers/friends`; access helper filtering | Composer audience selector and post badges | Implemented | Private-profile audience rules are centralized in `social/access.py`. |
| F-022 | Image/video upload | `image` ImageField ≤10 MB; `video` FileField ≤100 MB | Composer preview, upload progress, media viewer | Implemented | Multi-image `PostImage` has no writer. |
| F-023 | Multi-image gallery | `PostImage` model; read-only serializer field | Viewer reads `post.images` when present | Backend only / Not reachable | No upload endpoint; images-only post can fail serializer validation. |
| F-024 | Drafts | `is_draft`; `GET /api/posts/?drafts=true` | No draft/scheduling UI found in `frontend/src`; composer sends no `is_draft` field | Backend only / Partial | `drafts=true` returns all authored posts, not only drafts. |
| F-025 | Scheduling | `scheduled_for`; visibility filter hides future posts | No scheduler control, composer field, or publisher job found | Backend only / Partial | Publication job is `[NOT VERIFIED - USER CONFIRMATION REQUIRED]`; none found in source. |
| F-026 | Pinning | `POST /api/posts/<pk>/pin/`; `is_pinned` field | Home owner menu toggle | Partial | Feed/profile ordering does not consume the flag. |
| F-027 | Reposts | `POST /api/posts/<pk>/repost/`; `repost_of` FK | Home menu action and badge | Partial | Idempotent; own-post repost rejected; no notification. |
| F-028 | Bookmarks | `Bookmark` model; toggle endpoint; `?bookmarked=true` | `Bookmarks.jsx` and `PostActions.jsx` | Implemented | Toggle UI is not optimistic; errors rely on global interceptor. |
| F-029 | Hashtags | `Hashtag` model; regex sync on post create/update | No hashtag UI or browse endpoint | Backend only | Hashtags are derived from post text only. |
| F-030 | Polls | `Poll`, `PollOption`, `PollVote`; vote endpoint with view-level single-vote check | No poll composer, option list, or vote UI found | Backend only / Partial | No poll CRUD; DB uniqueness is per option, not per poll. |
| F-031 | Reports | `PostReport` model; create-only endpoint | Home report form | Partial | No status, resolve endpoint, moderation queue, or duplicate guard. |
| F-032 | Post detail deep link | `GET /api/posts/<pk>/`; visibility checks | `PostDetail.jsx` | Implemented | Comments are not paginated. |
| F-033 | Share | No dedicated backend endpoint | Web Share API/clipboard in home and bookmarks | Implemented (client-side) | Share count is local/page-owned; no server-side share record. |

## 5. Likes, comments, mentions, and social graph

| ID | Feature | Backend evidence | SPA / admin evidence | Status | Gap / caveat |
| --- | --- | --- | --- | --- | --- |
| F-034 | Likes | Like toggle endpoint; unique `(post,user)`; notification producer | Optimistic like in `PostActions.jsx` | Implemented | Busy state and rollback present. |
| F-035 | Comments | `GET/POST /api/social/posts/<pk>/comments/`; block and audience checks | Lazy comment panel in `PostActions.jsx` | Implemented | No pagination. |
| F-036 | Replies | `parent` FK with same-post validation | Threaded replies with cycle protection | Implemented | Deep threads can become visually dense. |
| F-037 | Comment edit/delete | Owner-only `PATCH/DELETE /api/social/comments/<pk>/` | Owner controls in comment UI | Implemented | Uses confirm dialog for delete. |
| F-038 | Mentions | Regex extraction; `Mention` model; notification producer | Typing `@username` produces mentions; no picker/highlight UI | Partial | Regex can capture trailing punctuation, causing invalid lookup. |
| F-039 | Comment reactions | `CommentReaction` model; toggle endpoint | No UI found | Backend only / Partial | No notification; model not registered in admin. |
| F-040 | Follow/unfollow | Follow toggle endpoint; unique directional follow; notification producer | Profile and search actions | Implemented | Block checks centralized. |
| F-041 | Followers/following lists | `GET /api/social/users/followers/`, `/following/` | `Connections.jsx` tabs | Implemented | Pagination metadata ignored by UI. |
| F-042 | Friend requests | Create/list/accept/reject/cancel endpoints; status + checks + indexes | `FriendRequests.jsx`, profile actions, right rail | Implemented with caveats | No notification on accept/reject; rejected request can be resurrected on resend; outgoing badge hard-coded to 0. |
| F-043 | Friends list/unfriend | `GET /api/social/friends/`, `DELETE /api/social/friends/<id>/` | `Connections.jsx` | Implemented | Block-aware. |
| F-044 | Blocks | Block toggle/list; self-block check; centralized filtering | Block/unblock on `UserProfile.jsx` | Implemented effect / Partial UI | History retained by design; no block-list screen. |

## 6. Stories

| ID | Feature | Backend evidence | SPA evidence | Status | Gap / caveat |
| --- | --- | --- | --- | --- | --- |
| F-045 | Story creation | `POST /api/users/stories/`; media ≤25 MB; server-set 24 h expiry; privacy choice | Creation dialog in `Stories.jsx` | Implemented | No edit/delete endpoints. |
| F-046 | Story list/visibility | `GET /api/users/stories/`; privacy, private profile, block, expiry filters | Grouped story strip; own story first | Implemented | Viewed IDs are component-local and reset on remount. |
| F-047 | Story view tracking | `POST /api/users/stories/<pk>/view/`; unique `(story,viewer)` | Viewer calls endpoint on display | Implemented | Viewer state not persisted across remount. |
| F-048 | Story viewer UX | N/A | 5-second auto-advance, pause/resume, keyboard nav, reduced motion, video handling | Implemented | Uses avatar thumbnails rather than story media previews. |
| F-049 | Story reactions | `StoryReaction` model; seven reaction types; react/list endpoints | No reaction UI found | Backend only / Partial | Reaction POST emits notification even on update; preference key exists. |
| F-050 | Story edit/delete | No endpoints found | No UI found | Not Found | `[NOT VERIFIED - USER CONFIRMATION REQUIRED]` whether required. |

## 7. Notifications

| ID | Feature | Backend evidence | SPA evidence | Status | Gap / caveat |
| --- | --- | --- | --- | --- | --- |
| F-051 | Notification list | `GET /api/notifications/`; newest first; hidden target IDs masked | `Notifications.jsx` with type-specific copy and deep links | Implemented | No pagination. |
| F-052 | Mark one/all read | `PATCH /api/notifications/<pk>/read/`, `POST /read-all/` | Buttons and local state update | Implemented | No WebSocket event emitted for read state. |
| F-053 | Unread count | `GET /api/notifications/unread-count/` | Navbar polls every 60 s; custom events trigger refresh | Implemented | Probe response discarded in one client path. |
| F-054 | Notification preferences | `NotificationPreference` model; `GET/PATCH /api/notifications/preferences/` | `NotificationSettingsDialog.jsx` with eight switches | Implemented | Optimistic UI with rollback. |
| F-055 | WebSocket delivery | `ws/notifications/?token=<access>`; consumer joins recipient group | Reconnect/backoff and live prepend in `Notifications.jsx` | Implemented | Read actions are not pushed to other clients. |
| F-056 | Producer coverage | Likes, comments, replies, mentions, follows, friend requests, messages, story reactions | N/A | Partial | Missing for accept/reject, comment reactions, reposts, pinning; duplicate risk on story reaction update. |

## 8. Messaging

| ID | Feature | Backend evidence | SPA evidence | Status | Gap / caveat |
| --- | --- | --- | --- | --- | --- |
| F-057 | Direct conversation list | `GET /api/chat/conversations/`; blocked pairs excluded | `Messages.jsx` conversation list with local search and unread badges | Implemented | No pagination; IDs coupled to peer user IDs. |
| F-058 | Direct message history | `GET /api/chat/conversations/<user_id>/`; soft-deleted excluded | Date-separated message list | Implemented | No history pagination. |
| F-059 | Send message REST | `POST /api/chat/conversations/<user_id>/`; optional attachment ≤25 MB | REST fallback send with FormData | Implemented | Attachment-only sends are impossible in UI because text is required. |
| F-060 | Send message WebSocket | `ws/chat/<user_id>/?token=<access>`; permission recheck; persist; notify; broadcast | Live send with reconnect backoff | Implemented | Query-string token log-leak risk. |
| F-061 | Typing and presence | Client `typing` event; server presence/typing broadcasts | Indicators in message header/list | Implemented | Presence on rejected socket may be false-negative. |
| F-062 | Read receipts | `POST /api/chat/conversations/<user_id>/read/`; broadcast message IDs | Opening conversation marks read; receipt frames rendered | Implemented | Read action emits no notification. |
| F-063 | Message edit/delete API | `PATCH/DELETE /api/chat/messages/<pk>/`; soft delete; WS update/delete frames for DMs | WS handlers render update/delete frames; no UI controls to trigger them | Partial | Client-supplied `deleted_at`/`edited_at` writability should be reviewed. |
| F-064 | Group conversations | `GroupConversation`, `GroupMembership`; group REST list/create/messages | No group UI found | Backend only / Partial | No group WebSocket; role/mute/archive fields unused; no membership management endpoints. |

## 9. Administration and platform

| ID | Feature | Backend evidence | Admin/template evidence | Status | Gap / caveat |
| --- | --- | --- | --- | --- | --- |
| F-065 | Custom admin site | `SocialConnectAdminConfig` → `SocialConnectAdminSite` (`config/admin.py:1-5`, `admin_site.py:21`); custom URLs at `:27-45` | Branded header/title/index template; permission-aware navigation groups | Implemented | Not part of React SPA. |
| F-066 | Live dashboard KPIs | `admin_metrics.dashboard_kpis()` (`admin_metrics.py:209-374`) aggregates 12 real-data cards with 30-day trend comparisons | Dashboard template cards with links | Implemented | Pending reports is total reports (no status field); likes card URL maps to Posts changelist (`admin_site.py:519`). |
| F-067 | Activity charts | `dashboard_series()` six-month registrations/posts; analytics daily/monthly real aggregates | Canvas line/bar/donut charts; data embedded via `json_script`; no client fetch | Implemented | Active users are refresh-token proxies, not live presence; some computed values are unrendered. |
| F-068 | Analytics page | Permission-gated view (`admin_site.py:90-137`); `?range=7|30|90`, invalid → 30 | Analytics template and JS | Implemented | Browser smoke verification is `[NOT VERIFIED - USER CONFIRMATION REQUIRED]`. |
| F-069 | Roles page | Superuser or `auth.view_group` gate; Django groups annotated with user/permission counts | Roles template | Implemented | Display-only; page states it does not grant or change privileges. |
| F-070 | System status | Superuser-only; DB connection check, channel/ASGI/DEBUG facts, last 8 `LogEntry` rows | System template | Implemented | Report-only; Redis status is `bool(REDIS_URL)`, no Redis ping or socket handshake. |
| F-071 | Real activity history | Django `LogEntry` queried at `admin_site.py:198-201`, `:552-557` | Admin history UI | Implemented | `AdminAction` is dormant: no actor, no writer, not admin-registered. |
| F-072 | Report moderation | `PostReport` create-only; no status/resolve endpoint | Dashboard can count reports only | Partial / Not Found | Moderation lifecycle is `[NOT VERIFIED - USER CONFIRMATION REQUIRED]`. |
| F-073 | PWA app shell | `public/sw.js`, `manifest.webmanifest` | Registered in production by `main.jsx` | Partial | No offline data, push, install prompt, update flow, or 192/512 PNG icons. |
| F-074 | Theme | CSS custom properties; navbar and admin JS toggles | Persistent light/dark theme using `socialconnect-theme` in SPA and `sc-admin-theme` in admin | Implemented | Manifest/meta colours may be inconsistent. |
| F-075 | Frontend automated tests | N/A | No test files and no `npm test` script | Not Found | Vitest/jsdom/@testing-library installed but unused. |
| F-076 | API schema export | No committed OpenAPI artifact found | No Swagger/Redoc route found | Not Found | `[NOT VERIFIED - USER CONFIRMATION REQUIRED]` whether schema export is required. |
| F-077 | Dead/unwired frontend source | N/A | `Profile.jsx`, `CreatePost.jsx`, `AuthWelcomePanel.jsx`, `formErrors.js`, `App.css`, unused assets, and `icons.svg` have no live import/reference | Not wired | Document as dead source only; do not describe as active features. |

## 10. End-to-end journey coverage

| Journey | Coverage | Assessment |
| --- | --- | --- |
| Register → login → edit profile → browse feed → post → like/comment → logout | Complete route/component chain | Implemented with minor caveats |
| Search user → follow / friend request → message → notification | Complete for direct flows | Implemented with minor caveats |
| Create story → view story → react | Creation/view complete; reaction UI missing | Partial |
| Report post → admin review | Submission works; no status/moderation action | Partial |
| Create poll → vote | Vote endpoint only | Backend only |
| Create group → send group message → receive live | REST only; no group UI or WebSocket | Backend only / Partial |
| Password reset via UI | REST only; no SPA confirm route | Backend only |
| Admin analytics review | Custom admin implemented | Implemented; browser verification unknown |
| Offline/PWA usage | App-shell caching only | Partial |
| Production deployment | Settings support only | Needs Verification |

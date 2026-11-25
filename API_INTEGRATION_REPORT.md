# SocialConnect API Integration Audit

**Date:** 2026-11-24  
**Target:** `C:\Django project\social media app`  
**Method:** Read-only audit of all React route/API call sites and all Django REST Framework routes, serializers, permissions, and models; followed by minimal safe fixes and full regression testing.

## Classification summary

| Classification | Features |
|---|---|
| **Fully Integrated** | Registration, login, JWT refresh/rotation, logout, profile retrieval/edit, profile picture/cover upload and removal, public profile, user posts, global feed with pagination, post create/edit/delete, likes, nested comments, bookmarks, reposts, pinning, reports, stories, friend requests, follow/unfollow, connections lists, user search, notifications list/read/read-all/preferences, unread counts, direct chat REST + WebSocket, message attachments, real-time typing/presence/read receipts/message edit/delete, custom Django admin. |
| **Partially Integrated** | Notification preferences include `story_reactions` but no backend event ever emits that type; story media type is inferred from the URL extension; chat WS token still uses a query parameter; a few chat endpoints are fetched more than once per mount; protected SPA routes check only token presence; media serving outside `DEBUG` still requires deployment configuration. |
| **Backend Only** | Poll voting, comment reactions, mutual friends, block list, password change/reset/deactivate endpoints, group conversations/group messages, message edit/delete UI actions, drafts/scheduled post listing (`?drafts=true`), hashtag synchronization, report records, resending story-reaction notifications. |
| **Frontend Only** | None. Every live frontend API call maps to a real backend route. |
| **Not Implemented** | `/explore` and `/settings` SPA routes, polls UI, group chat UI, hashtag UI, story-reaction producer, public report moderation workflow. |
| **Blocked / Needs Product Decision** | Report moderation statuses, persisted admin `AdminAction` audit writer, automatic role assignment, unordered-pair friend-request DB constraint, one-vote-per-poll DB constraint, private-profile discoverability policy. |

## Verified request/response contract

All live frontend requests were checked for endpoint path, HTTP method, auth header, payload keys, response fields, state update, error handling, and loading/empty states.

- **No missing live endpoint:** every routed frontend call (`api.get/post/patch/delete`) resolves to an existing DRF route.
- **No incorrect method:** all methods match the backend view implementation.
- **Auth is consistent:** axios adds `Authorization: Bearer <access>`; non-auth endpoints use `AllowAny`; all other API views use `IsAuthenticated`.
- **Object-level authorization:** verified for post edit/delete, comment edit/delete, notifications, friend requests, chat messages, conversations, and admin custom views.
- **Media URLs:** shared `getMediaUrl`/`API_ORIGIN` helper is used by routed pages; the one hardcoded legacy helper in `Profile.jsx` was replaced.

### Important fixes made after the audit

| Flow | Before | After |
|---|---|---|
| Story upload | Frontend did not send `expires_at`, but serializer required it → 400 | `expires_at` read-only; backend sets 24 h expiry; media/text validation added |
| Block/unblock profile | Post-block refetch got 404 and hid Unblock | Local optimistic `is_blocked` state |
| Feed refresh | `nextPageUrl` became stale when pages were preserved | Updated in both branches |
| Repost | Local share count incremented on idempotent 200 responses | Incremented only on 201 |
| Report reason | One shared textarea value for all posts | Per-post `reportReasons` map |
| MediaViewer | Undefined `src` prop on several pages; no video support | Prop removed where unused; video supported |
| Profile store | `force: true` could be skipped; misleading error text | Force honored; generic error text |
| Password reset | Reset token returned to unauthenticated caller | Generic response + email; token never in response |
| Refresh tokens | Survived password change/reset/deactivation | Blacklisted in all three flows |
| Chat attachment | Backend field existed, no UI/render | Upload control, validation, preview/link rendering |
| Chat WS message shape | Missing `sender_username` | Added; added edit/delete events and non-string guard |
| Group messages | Messages from blocked members remained visible | Excluded by blocker set |
| Notifications | Raw post/comment IDs could leak inaccessible targets | References nulled when target is not visible |
| Query performance | N+1 on post lists, search, followers/following, notifications | Shared prefetch helper and `select_related` added |
| Drafts | Author could create but not retrieve own draft | Author detail/list access with `?drafts=true` |

## Endpoint ownership map

| Area | Backend | Frontend |
|---|---|---|
| Auth/profile | `backend/users/urls.py`, `views.py`, `serializers.py` | `src/pages/Login.jsx`, `Register.jsx`, `EditProfile.jsx`, `src/api/axios.js`, `profileStore.js`, `src/components/navbar.jsx` |
| Posts/feed | `backend/posts/*`, `backend/social/views.py` | `src/pages/home.jsx`, `PostDetail.jsx`, `Bookmarks.jsx`, `src/components/PostActions.jsx` |
| Social graph | `backend/social/*` | `src/pages/UserProfile.jsx`, `UserSearch.jsx`, `FriendRequests.jsx`, `Connections.jsx`, `src/components/AppShell.jsx` |
| Chat | `backend/chat/*`, `config/asgi.py` | `src/pages/Messages.jsx`, `src/components/navbar.jsx` |
| Notifications | `backend/notifications/*` | `src/pages/Notifications.jsx`, `src/components/NotificationSettingsDialog.jsx`, `navbar.jsx` |
| Stories | `backend/users/views.py`, `serializers.py` | `src/components/Stories.jsx` |
| Admin | `backend/config/admin_site.py`, `admin_metrics.py` | Django-rendered admin (not an SPA route) |

## Verification results

- `manage.py check`: **PASS**
- `manage.py makemigrations --check --dry-run`: **No changes detected**
- `manage.py test --keepdb`: **60 passed, 0 failed, 0 skipped** (347.100 s)
- `npm.cmd run lint`: **PASS**
- `npm.cmd run build`: **PASS** (105 modules; CSS 123.80 kB / gzip 23.08 kB; JS 451.58 kB / gzip 135.16 kB)

No database reset, destructive migration, record deletion, `.env` overwrite, mock data, duplicate page/component, or endpoint removal was performed.

## Not verified in this environment

- Authenticated multi-account browser WebSocket sessions.
- Redis multi-worker channel-layer behavior.
- Production media serving with `DJANGO_DEBUG=False` behind a reverse proxy/object storage.
- Interactive mobile/tablet browser smoke tests after the final CSS changes.
- Email delivery through a real SMTP provider (tests used Django's locmem backend).

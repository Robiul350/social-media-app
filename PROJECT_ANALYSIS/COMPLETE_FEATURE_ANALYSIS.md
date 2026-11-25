# Complete Feature Analysis

## Method and status model

This feature analysis is based on direct inspection of the checked-in backend and frontend source. It does not rely on historical completion reports except where those reports are explicitly cited as claims.

| Status | Meaning in this document |
| --- | --- |
| **Implemented** | Backend route/model logic and reachable SPA behaviour are both present, with no known blocking gap in the primary flow. |
| **Partial** | Code exists, but one part of the end-to-end flow, UI, notification, ordering, or validation is incomplete or inconsistent. |
| **Backend only** | A working REST/WebSocket/model capability exists in Django, but no corresponding SPA screen or action was found. |
| **Planned / documented** | Mentioned in existing reports or design notes, but not proven in the active source. |
| **Not Found** | No supporting route, model, endpoint, component, or job was found in the inspected source. |
| **Needs Verification** | Runtime, environment, or deployment evidence would be required before making a claim. |

Historical documents contain conflicting status claims (for example, stories are called both “integrated” and “not integrated”). Where source and report disagree, source wins.

---

## Executive feature summary

| Domain | Backend | SPA | Overall status | Main caveat |
| --- | --- | --- | --- | --- |
| Registration, login, JWT refresh, logout | Complete | Complete | **Implemented** | Tokens stored in `localStorage`; route guard checks token presence only. |
| Password change/reset/deactivate | Complete API | No dedicated reset/deactivate screens | **Backend only / Partial** | Reset link points to an unrouted frontend path; email configuration not verified. |
| Profile CRUD and privacy | Complete | Complete | **Implemented** | No retry on profile load failure; `is_verified` admin-only. |
| User search and suggestions | Complete | Complete | **Implemented** | Search has a debounce/ref bug that can leave loading stuck. |
| Posts CRUD, drafts, audience | Complete | Complete | **Implemented** | `?drafts=true` returns all authored posts, not only drafts. |
| Polls | Vote endpoint only | No UI | **Backend only / Partial** | No poll CRUD; DB uniqueness is per option, not per poll. |
| Pinning | Toggle endpoint | Home menu toggle | **Partial** | `is_pinned` has no effect on feed/profile ordering. |
| Reposts | Toggle endpoint | Home menu action | **Partial** | No notification; own-post repost rejected; idempotent. |
| Reports | Create endpoint | Report form on feed | **Partial** | No status field, moderation workflow, or resolve endpoint. |
| Hashtags | Derived via regex | No UI | **Backend only** | No dedicated browse/search endpoint or page. |
| Scheduled posts | Field + visibility filter | Composer does not expose it | **Backend only / Partial** | No publisher job or scheduler UI. |
| Multi-image uploads | `PostImage` model + read-only field | Gallery reads `post.images` | **Backend only / Not reachable** | No API writer; post validation ignores images-only posts. |
| Likes and bookmarks | Complete | Complete | **Implemented** | Bookmark has no optimistic UI; errors share global state. |
| Comments, replies, mentions | Complete | Complete | **Implemented** | Mention regex captures trailing punctuation. |
| Comment reactions | Toggle endpoint | No UI | **Backend only / Partial** | No notification. |
| Follow / friends / blocks | Complete | Complete | **Implemented** | Block preserves history by design; no block-list screen. |
| Friend-request responses | Accept/reject endpoints | Complete | **Partial** | No notification to sender on accept/reject. |
| Stories | Full REST API | List/create/view UI | **Partial** | No reaction UI or story edit/delete; duplicate notifications on reaction update. |
| Notifications | Full REST + WS | Full list/read/preferences UI | **Implemented** | Read actions emit no WebSocket update; no pagination. |
| Direct chat | REST + WS | REST + WS UI | **Implemented** | Attachment-only sends are impossible; no message edit/delete UI. |
| Group chat | REST models/endpoints | No UI | **Backend only / Partial** | No group WebSocket; membership role/mute/archive unused. |
| Custom admin | Dashboard/analytics/roles/system | Django admin, not SPA | **Implemented** | Reports KPI count stale; likes KPI link wrong; no browser smoke evidence. |
| PWA/offline shell | Service worker/manifest | Registered in production | **Partial** | Minimal manifest; no offline data strategy. |
| Deployment/production hardening | Not Found in source | Not applicable | **Needs Verification** | No production static/media/ASGI process config in checkout. |

---

## 1. Identity and access

### 1.1 Registration

- **Backend evidence:** `POST /api/users/register/` uses `RegisterSerializer`; username/email uniqueness and Django password validation are applied. A `Profile` is auto-created by `users/signals.py`.
- **SPA evidence:** `frontend/src/pages/Register.jsx` posts `username`, `email`, `password`, `password2`, validates password length and match locally, then redirects to `/login` with a success notice.
- **Status:** **Implemented**.
- **Gaps:** Form labels are not programmatically associated with inputs; error container lacks `role="alert"`; no password visibility toggle.

### 1.2 Login, refresh, and logout

- **Backend evidence:** `POST /api/users/login/` returns user identity plus SimpleJWT access/refresh tokens. `token/refresh/` rotates and blacklists the previous refresh token. `logout/` blacklists the supplied refresh token.
- **SPA evidence:** `api/axios.js` attaches bearer tokens, refreshes once on 401, shares concurrent refresh promises, clears session on failure, and dispatches `socialconnect:auth-change`. `Login.jsx` persists four localStorage keys.
- **Status:** **Implemented**.
- **Gaps:** Username-only login despite the user model docstring referring to email-based authentication; no email login. Tokens in `localStorage` are XSS-readable. Route guards check only token presence, not validity.

### 1.3 Password and account lifecycle

| Feature | Backend | SPA | Status |
| --- | --- | --- | --- |
| Change password | `POST /api/users/password/change/`, revokes all refresh tokens | No screen found | **Backend only** |
| Request reset | `POST /api/users/password/reset/`, generic response, emailed link | No `/forgot-password` route found | **Backend only / Partial** |
| Confirm reset | `POST /api/users/password/reset/confirm/` | No `/password-reset-confirm/` route found | **Backend only / Partial** |
| Deactivate | `POST /api/users/account/deactivate/` | No account-deactivation screen found | **Backend only** |
| Email verification | `User.email_verified` field exists | No endpoint or UI | **Not Found** |

**Risk:** password-reset `send_mail(..., fail_silently=True)` is called while settings define no `EMAIL_BACKEND`/`DEFAULT_FROM_EMAIL`; the API always reports success. This is **Needs Verification** at runtime but a silent-failure risk in source.

---

## 2. Profiles and discovery

### 2.1 Own profile

- **Backend:** `GET/PATCH /api/users/profile/` with image upload/removal, privacy fields, `allow_comments`, `allow_messages`, social links, education/work. `is_verified` is read-only.
- **SPA:** `EditProfile.jsx` edits all main fields with previews and client-side image checks; `Navbar` uses a shared profile store; `UserProfile.jsx` renders the active profile.
- **Status:** **Implemented**.
- **Gaps:** No retry control after profile load failure; invalid file selection does not disable submit; GET has no abort controller; `Profile.jsx` is an unrouted legacy duplicate.

### 2.2 Public profile and relationship state

- **Backend:** `GET /api/users/<pk>/` returns `PublicProfileSerializer` with counts, follow state, friendship status, `can_view_profile`, `can_message`, and `is_blocked`. Private profiles mask profile details; blocked users return 404.
- **SPA:** `UserProfile.jsx` renders cover/avatar media viewer, bio, location, website, stats, edit/message/follow/friend/block controls, and confirmation dialogs.
- **Status:** **Implemented**.
- **Gaps:** Friend actions assume `friend_request_id` exists; `coverLoadFailed` is never reset; no explanation when messaging is disabled; no post pagination.

### 2.3 Search and suggestions

- **Backend:** `GET /api/users/search/` supports `?suggested=true` and `?search=`/`?q=`; excludes self and blocked users; suggestions also exclude followed accounts.
- **SPA:** `UserSearch.jsx` mirrors query into URL, debounces requests, exposes follow/friend shortcuts; navbar/sidebar/right rail use suggested users.
- **Status:** **Implemented** with a known state bug.
- **Gaps:** Render-phase `setState` during URL sync; abort/ref path can leave UI stuck loading; no reject control for incoming requests; no pagination.

---

## 3. Posts and content interactions

### 3.1 Post creation, editing, and visibility

- **Backend:** `PostListCreateView` and `PostDetailView` support CRUD, `audience`, `is_draft`, `is_pinned`, `scheduled_for`, image/video upload, hashtag sync, and author-only writes.
- **SPA:** `home.jsx` composer supports text, image/video, audience selection, upload progress, refresh, pagination, edit/delete menu, media viewer, share, report, repost, and pin.
- **Status:** **Implemented** core flow; several extensions partial.
- **Gaps:** `?drafts=true` returns all authored posts; scheduled posts have no publisher; `is_pinned` has no ordering effect; empty edit rejected when media exists only in `post.images`; shared error state across flows; initial feed request has no abort controller.

### 3.2 Likes, comments, mentions, and bookmarks

- **Backend:** Like toggle with notification; comment list/create with parent validation, block checks, profile comment policy, mention extraction, and comment/reply notifications; comment detail owner-only writes; bookmark toggle and bookmarked feed filter.
- **SPA:** `PostActions.jsx` on home, bookmarks, post detail, and profiles provides optimistic likes, lazy comments, nested replies, edit/delete, counts, and bookmark action.
- **Status:** **Implemented**.
- **Gaps:** Mention regex `@([A-Za-z0-9_.-]+)` captures trailing punctuation, so `@user.` becomes an invalid lookup; bookmark errors rely on global interceptor; comments are not paginated.

### 3.3 Polls

- **Backend:** `Poll`, `PollOption`, `PollVote` models and `POST /api/posts/<pk>/poll/<option_id>/vote/`; one active vote per poll enforced in the view with `select_for_update`.
- **SPA:** No poll composer, option list, or vote control found.
- **Status:** **Backend only / Partial**.
- **Gaps:** No poll CRUD; `PollVote` uniqueness is `(option, user)`, not `(poll, user)`; concurrent votes may bypass view-level enforcement.

### 3.4 Reposts, reports, hashtags, scheduling, multi-image

| Feature | Source evidence | Status | Gap |
| --- | --- | --- | --- |
| Reposts | `RepostView`; home menu action | **Partial** | No notification; idempotent `get_or_create`; own posts rejected. |
| Reports | `PostReportView`; home report form | **Partial** | No status, resolve endpoint, moderation queue, or duplicate guard. |
| Hashtags | `Hashtag` model, `sync_hashtags()` on create/edit | **Backend only** | No hashtag page or search endpoint. |
| Scheduling | `scheduled_for` field and visibility filter | **Backend only / Partial** | No publisher job; no scheduler UI; included in `?drafts=true`. |
| Multi-image | `PostImage` model and read-only serializer field | **Not reachable** | No upload endpoint; images-only posts fail serializer validation. |

---

## 4. Stories

- **Backend:** `Story`, `StoryView`, `StoryReaction` models; list/create/view/react/reactions endpoints; privacy, 24-hour expiry, private-profile gating, and block filtering.
- **SPA:** `Stories.jsx` renders grouped strip, own story first, creation dialog with 25 MB media check and privacy selection, viewer with progress bars, pause/resume, keyboard navigation, reduced-motion support, views, and video handling.
- **Status:** **Partial**.
- **Why not fully implemented:** No reaction UI despite seven backend reaction types and a `story_reactions` preference; no story edit/delete; reaction update emits duplicate notifications; viewed IDs are component-local.
- **Documentation conflict:** Root README says stories are not integrated; later reports and current source show a real Stories component. Treat README wording as stale.

---

## 5. Social graph

### 5.1 Follow, friends, mutual friends

- **Backend:** Follow toggle, follower/following lists, friend-request send/list/accept/reject/cancel, friend list/unfriend, mutual friends. Uses `select_for_update` for request creation and block checks throughout.
- **SPA:** `UserSearch.jsx`, `UserProfile.jsx`, `FriendRequests.jsx`, and `Connections.jsx` cover the main flows with tabs, badges, keyboard navigation, and confirmations.
- **Status:** **Implemented** for primary flows; **Partial** for notifications.
- **Gaps:** Accept/reject emits no notification; rejected requests are silently resurrected to pending on a new send; outgoing tab badge hard-coded to 0; mutual friends and block list are backend-only.

### 5.2 Blocks

- **Backend:** Block create/delete/list; centralized block filtering in feed, profiles, search, comments, chat, and notifications. Check constraint prevents self-block.
- **SPA:** Block/unblock on `UserProfile.jsx`; no dedicated block-list screen.
- **Status:** **Implemented** effect; **Backend only** list management.
- **Note:** Block does not delete follow rows or message history by design; tests assert retention while read paths hide it.

### 5.3 Mentions and comment reactions

- **Backend:** Mention extraction on comment creation with notifications; `CommentReactionView` toggle/update.
- **SPA:** Mentions are produced by typing `@username` in comments, but there is no mention picker or highlight UI. Comment reactions have no UI.
- **Status:** **Partial / Backend only**.
- **Gaps:** Trailing punctuation bug; comment reactions emit no notification; `Mention` and `CommentReaction` are not registered in admin.

---

## 6. Notifications

- **Backend:** `Notification`, `NotificationPreference`, REST list/read/read-all/unread-count/preferences, WebSocket consumer, `create_notification()` pipeline with block checks, opt-outs, and on-commit `group_send`.
- **SPA:** `Notifications.jsx` with live status, type icons/messages, refresh, mark-one/mark-all, unread styling, and deep links; navbar polls unread counts and reacts to custom events; `NotificationSettingsDialog.jsx` exposes eight switches.
- **Status:** **Implemented**.
- **Gaps:** Read actions emit no WebSocket update; busy unread notification can navigate without being marked read; no pagination; unread-count probe response discarded.

### Notification producer coverage

| Producer | Notification emitted? | Status |
| --- | --- | --- |
| Like | Yes | Implemented |
| Comment / reply | Yes | Implemented |
| Mention | Yes | Partial due to regex punctuation bug |
| Follow | Yes | Implemented |
| Friend request send | Yes | Implemented |
| Direct message | Yes | Implemented |
| Story reaction | Yes, on every POST including updates | Partial / duplicate risk |
| Friend request accept/reject | No | Missing |
| Comment reaction | No | Missing |
| Repost | No | Missing |
| Pin | No | Missing |
| Story creation | No | Not expected by preference schema |

---

## 7. Messaging

### 7.1 Direct chat

- **Backend:** `Message` model with soft delete; REST conversation list/detail/create/read/unread count; direct WebSocket consumer with JWT query-token auth, presence, typing, read receipts, edit/delete broadcasts, permission recheck, and block/privacy guards.
- **SPA:** `Messages.jsx` with conversation list/search, unread badges, typing/online indicators, date separators, read receipts, attachment support, REST fallback send, reconnect backoff, and live edit/delete frame handling.
- **Status:** **Implemented** core direct chat.
- **Gaps:** Attachment-only messages cannot be sent; no UI controls for edit/delete despite WS event support; no history pagination; strict ID type comparisons; shared error state; reconnect probe result unused.

### 7.2 Group chat

- **Backend:** `GroupConversation`, `GroupMembership`, group create/list, group message list/create, blocked-member filtering, creator admin role.
- **SPA:** No group conversation screen, creation dialog, membership UI, or group WebSocket found.
- **Status:** **Backend only / Partial**.
- **Gaps:** No group WS route or broadcast; `role`, `muted`, and `archived` fields have no API consumer; no membership management endpoints; REST message edit/delete skips WS broadcast for group messages.

---

## 8. Custom admin

- **Backend:** `SocialConnectAdminConfig` → `SocialConnectAdminSite`; `admin_metrics.py` computes 12 real-data KPIs, six-month charts, analytics ranges, permission-gated aggregates, roles, system status, and unread notification badge.
- **Templates/static:** Custom topbar, searchable sidebar, dark theme, confirmation modal, toasts, canvas line/bar/donut charts, responsive layout, and reduced-motion rules.
- **Status:** **Implemented** dashboard/analytics/roles/system; **Partial** moderation.
- **Gaps:** Likes KPI links to Posts due to wrong changelist key; pending reports count all reports because `PostReport` has no status; `AdminAction` is not an audit source; no successful admin browser verification in historical reports; several older docs still say eight KPI cards.

---

## 9. Frontend shell and UX features

| Feature | Evidence | Status | Notes |
| --- | --- | --- | --- |
| Protected routing | `App.jsx` checks `localStorage.access` | Implemented | Presence-only guard, not validity check. |
| Three-zone desktop shell | `AppShell.jsx` | Implemented | Sidebar, main outlet, right rail. |
| Mobile drawer + bottom nav | `AppShell.jsx`, `index.css` | Implemented | Focus trap, body lock, Escape/backdrop close. |
| Theme switch | `navbar.jsx`, CSS custom properties | Implemented | Persisted in localStorage; manifest/meta colours inconsistent. |
| Unread counters | Navbar polls two endpoints every 60 s | Implemented | Not pushed over WebSocket. |
| Notification settings dialog | `NotificationSettingsDialog.jsx` | Implemented | Eight optimistic switches with rollback. |
| Confirm dialog | `ConfirmDialog.jsx` | Implemented | Focus trap, keyboard handling, busy/error slots. |
| Media viewer | `MediaViewer.jsx` | Implemented | Zoom, navigation, keyboard, failed media state. |
| Skeletons and empty states | Pages and CSS | Implemented | Consistent across most list screens. |
| Pagination | Home feed only | Partial | Other pages ignore `next`/counts. |
| Frontend tests | None | Not Found | Vitest/jsdom present but unused. |

---

## 10. PWA and supporting assets

- **Implemented:** `public/sw.js` precaches app shell, uses network-first navigation fallback, and avoids returning HTML for failed API GETs. `main.jsx` registers it only in production.
- **Partial:** `manifest.webmanifest` has basic name/start/display but only an SVG favicon and inconsistent theme colour.
- **Not Found:** Offline data caching, push notifications, install prompts, update flow, and 192/512 PNG icons.
- **Stale assets:** `frontend/README.md` is Vite boilerplate; `public/icons.svg` is unreferenced.

---

## 11. Planned / documented but not found in active source

| Claim from historical docs or field intent | Current finding |
| --- | --- |
| `/explore` SPA page | Not Found; exploration is `/search`. |
| `/settings` SPA page | Not Found; settings are dialogs and Django admin. |
| Poll voting UI | Not Found; endpoint exists. |
| Group chat UI / group WebSocket | Not Found; REST API exists. |
| Hashtag browsing UI/API | Not Found; tags derived from post text only. |
| Report moderation and status workflow | Not Found; create-only endpoint. |
| Story reaction UI | Not Found; backend endpoint and preference exist. |
| Scheduled-post publisher job | Not Found; field and visibility filter exist. |
| Email verification flow | Not Found; field exists with no writer. |
| Multi-image upload endpoint | Not Found; model and read-only serializer field exist. |
| Frontend test suite | Not Found; dev dependencies installed only. |
| Production deployment configuration | Not Found in source; runtime topology Needs Verification. |

---

## 12. End-to-end journey coverage

| User journey | Coverage | Assessment |
| --- | --- | --- |
| Register → login → edit profile → browse feed → post → like/comment → logout | Complete route/component chain | **Implemented** |
| Search user → follow / friend request → message → receive notification | Complete for direct flows | **Implemented** with minor bugs |
| Create story → view story → react | Creation/view complete; reaction missing in UI | **Partial** |
| Report post → admin review | Report submission works; no status or moderation action | **Partial** |
| Create poll → vote | Vote endpoint only | **Backend only** |
| Create group → send group message → receive in real time | REST only; no WS/UI | **Backend only / Partial** |
| Reset password via UI | Backend API only; no SPA route for the emailed link | **Backend only** |
| Admin analytics review | Custom admin implemented | **Implemented**, browser smoke Needs Verification |
| Offline/PWA usage | App-shell caching only | **Partial** |

---

## 13. Final feature verdict

SocialConnect implements a broad core social network: identity, profiles, posts, media, social graph, stories, notifications, direct chat, and a substantial custom admin are all visibly wired. The project is best described as a **feature-rich functional prototype** rather than a finished production product.

The most important completion work is not new core functionality but closing integration and hardening gaps: story reactions, poll/group/report UIs, real-time read updates, attachment-only messages, pagination, frontend tests, email/deployment configuration, and the prioritized security and correctness fixes in `BUGS_AND_RECOMMENDATIONS.md`.

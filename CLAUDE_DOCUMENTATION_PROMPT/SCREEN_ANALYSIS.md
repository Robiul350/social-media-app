# Screen Analysis

This file inventories every reachable SPA screen, major reusable component, and custom admin screen proven by source. It distinguishes verified UI behavior from backend-only capabilities.

---

## 1. Routing model (`frontend/src/App.jsx`)

| Route | Screen component | Purpose | Guard / redirect |
| --- | --- | --- | --- |
| `/login` | `pages/Login.jsx` | Sign in | Public; authenticated users are redirected according to router logic. |
| `/register` | `pages/Register.jsx` | Create account | Public. |
| `/` | `pages/home.jsx` | Home: stories, composer, feed | Protected by presence of `localStorage.access`. |
| `/search` | `pages/UserSearch.jsx` | People discovery | Protected. |
| `/edit-profile` | `pages/EditProfile.jsx` | Profile and privacy settings | Protected. |
| `/messages` | `pages/Messages.jsx` | Conversation list / active chat | Protected. |
| `/messages/:userId` | `pages/Messages.jsx` | Direct conversation with a specific user | Protected. |
| `/notifications` | `pages/Notifications.jsx` | Notification feed and preferences entry point | Protected. |
| `/friend-requests` | `pages/FriendRequests.jsx` | Incoming/outgoing friend requests | Protected. |
| `/connections/:section` | `pages/Connections.jsx` | Friends / followers / following tabs | Protected. |
| `/bookmarks` | `pages/Bookmarks.jsx` | Saved posts | Protected. |
| `/profile` | Redirect | Sends user to `/users/<user_id>` from `localStorage.user_id` | Protected. |
| `/posts/:postId` | `pages/PostDetail.jsx` | Single-post detail with comments | Protected. |
| `/users/:userId` | `pages/UserProfile.jsx` | Public/own profile, relationship actions, posts | Protected. |
| `*` | Redirect | Unknown routes fall back to `/` | Protected fallback. |

`frontend/src/pages/Profile.jsx` exists in the source tree but is **not imported by `App.jsx`** and has no route. `UserProfile.jsx` is the active profile implementation.

There is no `/explore`, `/settings`, `/forgot-password`, `/password-reset-confirm`, `/groups`, `/polls`, or moderation SPA route in the verified router.

---

## 2. SPA shell and shared layout

### `components/AppShell.jsx`

| Aspect | Verified behavior |
| --- | --- |
| Desktop layout | Sticky navbar plus three-zone shell: left navigation, main `<Outlet />`, right rail. |
| Primary navigation | Home, Explore (`/search`), Friends (`/connections/friends`), Messages, Notifications. |
| Expandable navigation | Friend requests, Saved posts, My profile, notification settings/theme-related controls. |
| Right rail | Suggested people, incoming friend requests, friends, and shortcuts on home; generic discovery card elsewhere. |
| Mobile | Drawer plus fixed bottom navigation; modal behavior with focus trap, body scroll lock, backdrop/Escape close. |
| Unread counters | Polls `chat/unread-count/` and `notifications/unread-count/`, refreshed periodically and after custom events. |
| State coordination | Uses `profileStore.js` and custom window events such as `socialconnect:auth-change`. |

### `components/navbar.jsx`

| Aspect | Verified behavior |
| --- | --- |
| Brand/primary links | Brand mark, icon navigation, active state via `NavLink`. |
| People search | Header search that navigates to `/search`. |
| Unread badges | Chat and notification counts with error-tolerant fetching. |
| Theme | Light/dark toggle persisted in `localStorage`; CSS custom properties drive colors. |
| Notifications | Opens `NotificationSettingsDialog.jsx`. |
| Account menu | Profile, saved posts, settings entry, logout with `ConfirmDialog.jsx`. |
| Session behavior | Tracks `localStorage.access`; logout posts refresh token for blacklisting and clears session keys. |

---

## 3. Screen-by-screen analysis

### UI-SCR-001 — Login (`/login`)

- **Purpose:** Authenticate a registered user and establish a JWT session.
- **API:** `POST /api/users/login/` with `username`, `password`.
- **State:** username, password, loading, error, password visibility, route notice, intended destination from `location.state`.
- **Success:** Stores `access`, `refresh`, `user_id`, `username`; dispatches auth-change; redirects.
- **UX/AT:** Split auth layout rendered inline in `Login.jsx`; password visibility toggle. `AuthWelcomePanel.jsx` exists but is not imported.
- **Gaps:** No password-reset affordance; generic catch can swallow the explicit invalid-response message.

### UI-SCR-002 — Register (`/register`)

- **Purpose:** Create a new account.
- **API:** `POST /api/users/register/`.
- **Validation:** Local minimum password length and password match checks.
- **Success:** Redirects to `/login` with a notice.
- **Gaps:** Labels are not programmatically associated with inputs; error container lacks `role="alert"`.

### UI-SCR-003 — Home feed (`/`)

- **Purpose:** Stories, post composer, and paginated social feed.
- **APIs:** `GET /api/social/feed/?page=…`, post CRUD, bookmark, pin, repost, report, poll vote where exposed, stories endpoints via `Stories.jsx`.
- **Components:** `Stories`, local composer, post cards, `PostActions`, `MediaViewer`, `ConfirmDialog`, `UserAvatar`.
- **Composer:** Text, image/video, audience selection, previews, upload progress, validation (10 MB images, 100 MB videos from backend).
- **Feed:** IntersectionObserver pagination; refresh preserves loaded pages.
- **Post card:** Author link, audience badge, pinned/repost indicators, media gallery/video, owner menu (edit/pin/delete), non-owner menu (repost/report), share via Web Share API or clipboard.
- **Gaps:** Initial feed request has no abort controller; shared `error` state across edit/delete/share/report/repost/pin; editing rejects empty content when media exists only in `post.images`; report action uses one global `reporting` flag.

### UI-SCR-004 — Stories (embedded on home)

- **Purpose:** Create and view 24-hour stories.
- **Source:** `components/Stories.jsx`.
- **APIs:** `GET/POST /api/users/stories/`, `POST /api/users/stories/<id>/view/`.
- **UX:** Grouped strip; own story first; unseen ring; creation dialog with 25 MB media check and privacy selection; 5-second auto-advance; pause/resume; keyboard navigation; reduced-motion support; video handling; view count.
- **Gaps:** No reaction selector despite backend reaction endpoint; no story edit/delete; viewed IDs are component-local; thumbnails use avatars rather than story media previews.

### UI-SCR-005 — Post detail (`/posts/:postId`)

- **Purpose:** Focused single-post view with comments and standard actions.
- **Components:** `PostActions`, `MediaViewer`, `ConfirmDialog`.
- **APIs:** Post detail, likes, comments, bookmarks, repost/report/pin where applicable.
- **Gaps:** Comments are not paginated; shares of error state follow `PostActions`.

### UI-SCR-006 — User profile (`/users/:userId`)

- **Purpose:** View a public or own profile and manage relationship state.
- **Source:** `pages/UserProfile.jsx`.
- **APIs:** `GET /api/users/<id>/` or `profile/`, `GET /api/users/<id>/posts/`, follow, friend-request, block, unfriend.
- **UI:** Cover and avatar with media viewer; bio, location, website; counts; edit link for owner; follow/unfollow; friend-request send/cancel/accept/reject where applicable; block/unblock; conditional message link; posts list.
- **Accessibility:** Confirmation dialogs for destructive actions; media viewer keyboard support.
- **Gaps:** Friend actions assume `friend_request_id`; `coverLoadFailed` is never reset; message link is hidden with no disabled explanation; no post pagination.

### UI-SCR-007 — Edit profile (`/edit-profile`)

- **Purpose:** Edit identity, bio, privacy, permissions, and media.
- **API:** `GET/PATCH /api/users/profile/` with multipart upload/removal flags.
- **Fields:** first/last name, bio, location, website, social links, education/work, `is_private`, `allow_comments`, `allow_messages`, profile/cover image.
- **UX:** Previews, client-side image validation, removal controls, success event dispatch.
- **Gaps:** Load failure has no retry; invalid file selection does not disable submit; GET has no abort controller; no explicit cancel/back link.

### UI-SCR-008 — User search (`/search`)

- **Purpose:** Debounced people discovery.
- **APIs:** `GET /api/users/search/?search=…`, follow and friend actions.
- **UX:** URL-synchronized query, result cards with follow/friend shortcuts, suggested accounts.
- **Gaps:** Render-phase `setState` during URL sync; abort/cache-ref path can leave loading stuck; no incoming-request reject control; no pagination.

### UI-SCR-009 — Friend requests (`/friend-requests`)

- **Purpose:** Manage incoming and outgoing friend requests.
- **APIs:** `GET /api/social/friend-requests/?direction=…`, accept/reject/cancel.
- **UX:** ARIA tablist with keyboard arrow navigation; incoming count badge; tailored empty states.
- **Gaps:** Outgoing badge is hard-coded to `0`; no pagination.

### UI-SCR-010 — Connections (`/connections/:section`)

- **Purpose:** Browse friends, followers, and following.
- **APIs:** `GET /api/social/friends/`, `/api/social/users/followers/`, `/api/social/users/following/`.
- **UX:** Tabbed lists with profile links and unfriend/follow affordances.
- **Gaps:** Read-only for mutual friends; pagination metadata ignored.

### UI-SCR-011 — Bookmarks (`/bookmarks`)

- **Purpose:** Display saved posts with full post actions.
- **APIs:** `GET /api/posts/?bookmarked=true`, like/comment/bookmark/report/repost/pin as applicable.
- **UX:** Feed-like cards, refresh, media viewer, share, notices.
- **Gaps:** No pagination; notice is not auto-cleared or reset on refresh.

### UI-SCR-012 — Messages (`/messages`, `/messages/:userId`)

- **Purpose:** Direct messaging with real-time updates.
- **REST APIs:** Conversation list, history, send with optional attachment, read, unread count.
- **WebSocket:** `ws/chat/<user_id>/?token=<access>`; typing, presence, read receipt, message update/delete frames.
- **UX:** Conversation search, unread badges, online indicators, date separators, typing indicator, attachments, reconnect backoff, REST fallback send.
- **Gaps:** Attachment-only sends impossible; no UI controls for edit/delete despite frame handlers; no history pagination; strict ID type comparisons; shared error state; reconnect probe result unused.

### UI-SCR-013 — Notifications (`/notifications`)

- **Purpose:** Notification feed and read management.
- **REST APIs:** `GET /api/notifications/`, `PATCH /<id>/read/`, `POST /read-all/`, `GET /unread-count/`, preferences via settings dialog.
- **WebSocket:** `ws/notifications/?token=<access>` with reconnect backoff.
- **UX:** Type-specific icons/messages, unread styling, live status, refresh, mark-one/mark-all, deep links.
- **Gaps:** Busy unread notification can navigate without being marked read; no pagination; unread-count probe response discarded.

### UI-SCR-014 — Notification settings dialog (global)

- **Source:** `components/NotificationSettingsDialog.jsx`.
- **API:** `GET/PATCH /api/notifications/preferences/`.
- **Preferences:** likes, comments, replies, follows, friend_requests, messages, mentions, story_reactions.
- **UX:** Eight switches with optimistic update and rollback; focus trap.
- **Status:** Implemented. No dedicated `/settings` route.

---

## 4. Reusable component inventory

| Component | Source | Purpose | Verified behavior / notes |
| --- | --- | --- | --- |
| `AppShell` | `components/AppShell.jsx` | Authenticated layout and navigation | Three-zone desktop, drawer/bottom nav, right rail, focus trap. |
| `navbar` | `components/navbar.jsx` | Top navigation, search, badges, theme, account menu | Polls unread counts; opens settings/logout dialogs. |
| `AuthWelcomePanel` | `components/AuthWelcomePanel.jsx` | Auth marketing panel | Unused; no source import found. Login/Register render their own inline split layout. |
| `ConfirmDialog` | `components/ConfirmDialog.jsx` | Destructive-action confirmation | Focus trap, Escape/Tab handling, busy/error slots, `alertdialog` semantics. |
| `CreatePost` | `components/CreatePost.jsx` | Simple composer posting `multipart/form-data` to `posts/` | Unused; the active composer is inline in `home.jsx`. |
| `Icon` | `components/Icon.jsx` | Inline SVG icon set | Home, search, friends, messages, notifications, settings, etc. |
| `MediaViewer` | `components/MediaViewer.jsx` | Image/video lightbox | Zoom, next/previous, keyboard, failed media state, animated close. |
| `NotificationSettingsDialog` | `components/NotificationSettingsDialog.jsx` | Preference switches | Eight keys; optimistic update with rollback. |
| `PostActions` | `components/PostActions.jsx` | Like, bookmark, comments, replies, share | Optimistic like with rollback; lazy comments; nested replies with cycle protection. |
| `Stories` | `components/Stories.jsx` | Story strip, creator, viewer | Auto-advance, pause/resume, keyboard nav, reduced motion, view tracking. |
| `UserAvatar` | `components/UserAvatar.jsx` | Avatar with fallback and optional full-size viewer | Uses `getMediaUrl`; initial fallback; failed image state. |
| `useFocusTrap` | `hooks/useFocusTrap.js` | Modal keyboard focus containment | Tab wrapping; used by dialogs/drawer. |
| `formErrors` | `utils/formErrors.js` | DRF error normalization helpers | Unused; current pages implement local error flattening. |

Additional source files present but not imported/referenced: `frontend/src/App.css`, `frontend/src/assets/hero.png`, `frontend/src/assets/react.svg`, `frontend/src/assets/vite.svg`, and `frontend/public/icons.svg`. Treat them as dead/unwired assets, not active UI behavior.

---

## 5. Authentication, session, and API client behavior

| Concern | Verified behavior |
| --- | --- |
| API base | `VITE_API_BASE_URL || http://127.0.0.1:8000/api/`. |
| Media/WebSocket origin | `VITE_API_ORIGIN || apiBaseUrl`, normalized with `new URL(...).origin`. |
| Session keys | `access`, `refresh`, `user_id`, `username`; theme preference is `socialconnect-theme`. |
| Token injection | Axios request interceptor attaches `Authorization: Bearer <access>`. |
| 401 handling | Refresh once via `POST users/token/refresh/`, replay original request, share concurrent refresh promise, clear session on failure. |
| Session clearing | Removes four auth localStorage keys, dispatches `socialconnect:auth-change`, redirects to `/login` when appropriate. |
| Cross-component events | `socialconnect:auth-change`, `socialconnect:profile-change`, `socialconnect:refresh-counts`, and native `storage`. |
| Profile cache | `profileStore.js` exposes snapshot/subscribe/load/reset with in-flight de-duplication. |
| Route guard | Checks presence of `access` only; token validity is resolved by API refresh/clear flow. |

---

## 6. Accessibility and responsiveness

### Verified strengths

- Semantic landmarks and labelled controls across most screens.
- ARIA roles for dialogs, alertdialogs, switches, tabs, menus, status, and alerts.
- Focus traps and focus restoration in modal components.
- Keyboard handling for Escape, Tab, arrow keys, and story navigation.
- `sr-only` text for icon-only controls and loading/result announcements.
- Visible focus rings and high-contrast theme tokens.
- `prefers-reduced-motion` handling, including story auto-advance.
- Responsive breakpoints in `frontend/src/index.css` for desktop, tablet, mobile, and very small screens; hover effects limited to hover-capable devices.

### Verified gaps

- Register labels not programmatically associated with inputs.
- Some error messages lack `role="alert"`.
- No visible skip-to-content link.
- Profile menu "Saved posts" uses the Explore icon, weakening visual semantics.
- Deep comment threads have no collapse control.
- Form validation relies partly on browser-native `required` rather than a unified inline summary.

---

## 7. Custom admin screens (`backend/config/admin_site.py` and templates)

The admin is a Django site, not part of the React SPA. `SocialConnectAdminConfig` (`config/admin.py:1-5`) installs `SocialConnectAdminSite` (`config/admin_site.py:21`) at `/admin/` (`config/urls.py:18-20`). Identity strings are `SocialConnect Administration`, `SocialConnect Admin`, and `Dashboard`; the index template is `admin/socialconnect_index.html` (`admin_site.py:22-25`).

| Admin screen | URL / source | Permission gate | Purpose | Status / caveat |
| --- | --- | --- | --- | --- |
| Dashboard | `/admin/` → `admin/socialconnect_index.html` (`admin_site.py:84-88`) | `admin_view()` staff gate | 12 live KPI cards, six-month user/post charts, recent users/posts/admin activity | Implemented. Likes card URL maps to Posts changelist (`admin_site.py:519`); pending reports count is total reports because `PostReport` has no status field. |
| Analytics | `/admin/analytics/` (`admin_site.py:90-137`) | Staff plus any of 8 model permissions (`admin_site.py:92-105`, helper `:263-277`); `PermissionDenied` otherwise | Range-filtered real aggregates for `?range=7|30|90`; invalid values fall back to 30 days | Implemented. Some computed values (reaction distribution, cumulative likes/comments, several totals) are not rendered. Browser smoke verification is `[NOT VERIFIED - USER CONFIRMATION REQUIRED]`. |
| Roles | `/admin/roles/` (`admin_site.py:139-165`) | Staff plus superuser or `auth.view_group` | Shows Django groups/permission counts and current user's groups/permissions | Implemented; display-only. The page states it does not grant or change privileges. |
| System status | `/admin/system/` (`admin_site.py:167-205`) | Superuser only | DB connection check, channel-layer/ASGI/DEBUG facts, last 8 `LogEntry` rows | Implemented as report-only. Redis status is derived from `bool(REDIS_URL)` and WS status from `ASGI_APPLICATION`; no Redis ping or socket handshake is performed. |
| Model changelists | Standard Django admin from `super().get_urls()` (`admin_site.py:45`) | Per-model Django permissions | CRUD according to each registered `ModelAdmin` | Implemented. Chat admins, preferences, and `LogEntry` are effectively view-only; user deactivate/reactivate and notification read/unread actions are mutating and logged. |
| Activity history | Django `LogEntry` (`admin_site.py:198-201`, `:552-557`) | Activity permission where used | Real admin action history | Implemented. `AdminAction` is inert and is not the audit source. |

Global context injected into every admin page (`admin_site.py:47-82`) includes permission-aware navigation groups, admin avatar/role label, unread notification count, changelist search URLs, profile/system/analytics/frontend URLs, and `FRONTEND_URL` for "Back to website"/password-reset links. Navigation groups are `MAIN MENU`, `SOCIAL MANAGEMENT`, `MODERATION & GOVERNANCE`, and `SYSTEM` (`admin_site.py:302-494`).

### Admin data and charts

- 12 dashboard KPIs from `admin_metrics.dashboard_kpis()` (`admin_metrics.py:209-374`): total users, active users (refresh-token proxy), total posts/comments, pending reports (actually all reports), total likes, new registrations, pending friend requests, total/active/expired stories, and total story reactions.
- Trends compare the last 30 days with the previous 30 days; story cards intentionally have no trend.
- Dashboard charts are six-month registrations and posts (`admin_metrics.dashboard_series()`, `admin_metrics.py:145-152`).
- Analytics includes registrations/cumulative users, active-user proxy, posts, comments, likes, messages, notifications, reports, friend requests created/accepted, monthly active users, popular posts, and top users (`admin_metrics.py:377-570`).
- Permission masking uses `—` for KPI values, zero-filled chart arrays, `Restricted` table cells, and empty states for recent lists.
- Story-reaction metrics degrade to `—` when the table is absent, verified via introspection (`admin_metrics.py:158-166`, `:357-370`).
- No persisted login-event table exists; "Active Users" is explicitly described as a refresh-token proxy, not live presence.

### Admin client behavior

- `base_site.html` overrides Django's header/breadcrumbs and loads `socialconnect-premium.css` and `socialconnect-dashboard.js` with cache-bust `?v=10`.
- `socialconnect-dashboard.js` (722 lines) contains **no `fetch`/XHR/WebSocket calls**; all chart data is server-rendered through `json_script` and parsed from `#sc-dashboard-data` / `#sc-analytics-data`.
- JS provides theme toggle with `localStorage["sc-admin-theme"]`, mobile off-canvas nav, collapsible sidebar, sidebar filter, scoped global search form rewriting, confirmation modal, dismissible toast messages, and canvas line/bar/donut charts with tooltips and empty states.
- Accessibility attributes include `aria-label`, `aria-expanded`, `aria-current="page"`, `role="img"` on canvases, and `role="dialog"` on the modal. Reduced-motion CSS is present.
- Template inheritance: six local admin templates only — `base_site.html`, `nav_sidebar.html`, `socialconnect_index.html`, `analytics.html`, `admin_roles.html`, `admin_system.html`. The local `nav_sidebar.html` shadows Django's built-in sidebar for pages that include it. Runtime visual confirmation on built-in changelists is `[NOT VERIFIED - USER CONFIRMATION REQUIRED]`.

Admin static assets are served through Django static configuration; production static serving is `[NOT VERIFIED - USER CONFIRMATION REQUIRED]`.

---

## 8. Screen-to-feature status summary

| UI area | Status | Key limitation |
| --- | --- | --- |
| Auth, profile, feed, likes/comments, follow/friends/blocks, bookmarks, direct chat, notifications | Implemented with caveats | No frontend tests; limited pagination; several shared-state issues. |
| Stories list/create/view | Implemented with caveats | Reaction UI absent; viewed IDs not persisted. |
| Poll voting, story reactions, comment reactions, group chat, mutual friends, block-list screens, password lifecycle screens, moderation | Not Found in SPA | Backend capabilities exist for several items. |
| Admin dashboard/analytics/roles/system | Implemented with caveats | Not a SPA route; moderation lifecycle absent. |
| PWA | Partial | App-shell caching only. |

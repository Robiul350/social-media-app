# UI/UX Analysis

## Information architecture

The SPA exposes a consistent three-zone authenticated layout on desktop and a drawer/bottom-nav layout on mobile.

### Routes

| Route | Screen | Primary purpose |
| --- | --- | --- |
| `/login`, `/register` | Auth pages | Sign in / create account; public layout with navbar only. |
| `/` | Home | Stories, composer, paginated feed, post actions. |
| `/profile` | Redirect | Sends the user to `/users/:user_id` from `localStorage.user_id`. |
| `/users/:userId` | User profile | Public/current profile, relationship actions, posts, media. |
| `/posts/:postId` | Post detail | Single-post view with comments and reactions. |
| `/search` | User search | Debounced people search with follow/friend shortcuts. |
| `/edit-profile` | Edit profile | Profile fields, privacy, permissions, photo/cover upload. |
| `/messages`, `/messages/:userId` | Messages | Conversation list and real-time 1:1 chat. |
| `/notifications` | Notifications | Live notification feed and read actions. |
| `/friend-requests` | Friend requests | Incoming/outgoing request management. |
| `/connections/:section` | Connections | Friends / followers / following tabs. |
| `/bookmarks` | Bookmarks | Saved posts with standard post actions. |
| `*` | Redirect | Unknown routes return to `/`. |

`Profile.jsx` exists in the source tree but is **not imported by `App.jsx`** and has no route. `UserProfile.jsx` is the active profile implementation.

## Navigation model

### Desktop

- Sticky top navbar: brand, primary icon navigation, people search, unread badges, theme switch, notification settings, and account menu.
- Left sidebar: profile summary plus primary links; expandable “See more” group for friend requests, saved posts, my profile, settings.
- Right rail on `/`: suggested people, incoming friend requests, friends, and shortcuts. Other routes show a generic discovery card.
- Unread counters are fetched from `chat/unread-count/` and `notifications/unread-count/`, refreshed every 60 seconds and after custom events.

### Mobile

- Top bar collapses into brand, drawer trigger, theme/account controls.
- Fixed bottom bar: Home, People, Friends, Chat, Alerts, More.
- “More” popover exposes friend requests, saved posts, profile, and settings.
- Drawer is modal with focus trap, body scroll lock, backdrop/Escape close, and full navigation list.

## Screen-level UX

### Authentication

`Login.jsx` and `Register.jsx` use split auth layouts with a welcome panel/card. Login supports password visibility toggling and restores the intended destination from route state. Register performs client-side password length/match checks before POSTing to `users/register/`.

Findings:

- Register labels are not programmatically associated with inputs, and its error container lacks `role="alert"`.
- Login has no password-reset or “remember me” affordance despite backend password-reset endpoints.
- Login’s explicit invalid-response error is swallowed by its generic catch branch.

### Home/feed

The home page combines stories, composer, and feed in a single scroll:

- Stories are grouped by author, own story first, with unseen rings and a modal viewer.
- Composer supports text, image/video, audience selection, previews, upload progress, and validation (10 MB images, 100 MB videos).
- Feed loads `social/feed/?page=1`, uses an IntersectionObserver sentinel for pagination, and supports refresh while preserving already-loaded pages.
- Post cards expose author links, audience badges, pinned/repost indicators, media galleries/video, and `PostActions`.
- Owner menu supports edit, pin/unpin, delete; non-owner menu supports repost and report.
- Share uses Web Share API or clipboard; notices auto-dismiss.

Findings:

- The feed initial request has no abort controller.
- `error` is shared across edit/delete/share/report/repost/pin flows, causing cross-flow error leakage.
- Editing rejects empty content when media exists only in `post.images`.
- The report action uses one global `reporting` flag for all posts.
- `loggedIn` is derived during render from localStorage and does not subscribe to auth changes.

### Stories

The stories component is a strong interaction surface: creation dialog with media type/size checks, privacy selector, upload progress, grouped strip, 5-second auto-advance, pause/resume, keyboard navigation, reduced-motion support, views, and video end handling.

Findings:

- Viewed IDs are component-local and reset on remount.
- Reactions are not exposed in the UI, although backend story reactions and a preference key exist.
- The viewer uses avatar-only thumbnails rather than story media previews.

### Posts and comments

`PostActions.jsx` provides like (optimistic with rollback), bookmark, comments, threaded replies, comment edit/delete, counts, and share. Comments are grouped by parent with cycle protection and lazy loading on first expansion.

Findings:

- Bookmark action does not optimistic-update and has no auth pre-check; it relies on the API/global interceptor.
- Nested replies are rendered inline and can become visually dense on deep threads.
- `currentUserId` is read from localStorage at render time.
- Share count is displayed but repost increments are owned by the page rather than the component.

### Profiles

`UserProfile.jsx` is the substantive profile screen: cover/avatar media viewer, bio/location/website, stats, edit link for owners, follow/unfollow, friend request lifecycle, block/unblock, conditional message link, posts, and confirmations.

Findings:

- Message access is hidden when `can_message` is false, with no explanatory disabled state.
- Friend actions rely on `user.friend_request_id` without guarding missing IDs.
- Posts have no pagination.
- `coverLoadFailed` is never reset after a failure.
- The dead `Profile.jsx` implementation has a self-redirecting “Edit Profile” link and only basic media support.

### Search and connections

`UserSearch.jsx` provides debounced user search, URL-synchronised query state, follow toggles, and friend actions directly in results. `Connections.jsx` offers friends/followers/following tabs.

Findings:

- Search uses render-phase `setState` when syncing URL query.
- Search’s abort/cache-ref path can leave the UI stuck in a loading state after cancelling and repeating the same query.
- Search offers no reject action for incoming requests.
- Connections pages are read-only and ignore pagination metadata.

### Messages

`Messages.jsx` is the most complex real-time screen: conversation list with local search, unread badges, online indicators, chat history with date separators, typing indicator, read receipts, attachments, typing/presence/read/update/delete WebSocket frames, REST fallback send, and exponential reconnect.

Findings:

- Attachment-only messages cannot be sent: both the button and handler require non-empty text.
- WebSocket event handlers support message edit/delete, but the UI provides no controls to trigger them.
- Conversation list IDs are treated as peer user IDs; this matches current link construction but couples two concepts.
- Chat history has no pagination.
- Shared `error` state mixes loading, send, read, and socket failures.

### Notifications

`Notifications.jsx` shows type-specific icons/messages, unread styling, live status, refresh, mark-one/mark-all, and deep links to targets. Live updates arrive over WebSocket with reconnect backoff.

Findings:

- A busy unread notification can navigate without being marked read because `preventDefault()` happens after an early return.
- No pagination.
- Unread-count probe responses are discarded.

### Friend requests and bookmarks

`FriendRequests.jsx` has a well-structured ARIA tablist with keyboard arrow navigation, incoming count badge, accept/reject/cancel, and tailored empty states. `Bookmarks.jsx` mirrors the feed card layout with refresh, media viewer, sharing, and full post actions.

Findings:

- Neither page paginates.
- Bookmark `notice` is never auto-cleared or reset on refresh.
- Outgoing request tab badge is hard-coded to `0`.

### Edit profile

`EditProfile.jsx` supports all major profile fields and privacy/comment/message policy, with image validation, previews, removal flags, and optimistic event dispatch on success.

Findings:

- Load failure requires manual browser reload; no retry control.
- Invalid file selection does not disable submit.
- The GET request has no abort controller.
- No cancel/back link.

## Responsive behaviour

- Desktop: three-column shell; right rail hidden/collapsed at narrower widths.
- Tablet (`<=1180`, `<=1100`, `<=920px`): sidebar/rail adapt or collapse.
- Mobile (`<=760px` and below): drawer plus bottom navigation; cards stack; dialogs become full-width/stacked.
- Very small screens (`<=500`, `<=480`, `<=420`, `<=400px`): tighter spacing and typography.
- `prefers-reduced-motion` disables transitions/animations and story auto-advance.
- Hover effects are limited to hover-capable/pointer-fine devices.

## Accessibility assessment

### Strengths

- Semantic landmarks and labelled controls across most screens.
- ARIA roles for dialogs, alertdialogs, switches, tabs, menus, status, and alerts.
- Focus traps and focus restoration in modal components.
- Keyboard handling for Escape, Tab, arrow keys, and story navigation.
- `sr-only` text for icon-only controls and loading/result announcements.
- Visible focus rings and high-contrast text tokens.

### Gaps

- Register labels are not associated with inputs.
- Some error states use plain paragraphs without `role="alert"`.
- The profile-menu “Saved posts” item uses the Explore icon, weakening visual semantics.
- Content-heavy comment threads lack collapse controls.
- No visible skip-to-content link.
- Form validation relies partly on browser-native required fields rather than a unified inline validation summary.

## UX quality summary

| Dimension | Assessment |
| --- | --- |
| Visual polish | High: gradients, cards, skeletons, dark mode, animated dialogs, responsive tuning. |
| Consistency | Good across shared components; weakened by dead `Profile.jsx`, duplicated CSS, and inconsistent error handling. |
| Feedback | Strong: loading skeletons, notices, toasts in admin, optimistic updates, busy labels. |
| discoverability | Good: clear nav labels, right-rail suggestions, empty-state CTAs. |
| Accessibility | Above average for coursework, with a few concrete form and ARIA gaps. |
| Feature completeness | Core social flows are present; several backend capabilities lack UI. |
| Mobile | Well considered, but authenticated browser smoke testing is only historical/partial. |

## Priority UX improvements

1. Wire message send to allow attachment-only messages and expose edit/delete controls for supported WebSocket events.
2. Fix the search loading/cache-ref bug and move URL query synchronisation out of render.
3. Split shared error states per operation so one failure does not contaminate another dialog.
4. Add retry controls for profile/feed load failures and abort in-flight initial requests.
5. Add pagination to bookmarks, connections, notifications, friend requests, profiles, and chat history.
6. Remove or archive `Profile.jsx` to avoid confusion with the active `UserProfile.jsx`.
7. Add explicit disabled explanations where messaging is not permitted.
8. Replace duplicated CSS blocks with a single source of truth and align manifest/PWA theme tokens.

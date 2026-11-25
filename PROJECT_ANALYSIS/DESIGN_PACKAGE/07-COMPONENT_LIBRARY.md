# 07 — Component Library

## Purpose

This catalogue defines the reusable components for the proposed SocialConnect redesign. It maps current source components to proposed primitives and records anatomy, variants, states, props, interaction rules, and accessibility requirements.

**Existing implemented UI** components are grounded in source inspection. **Proposed** components are recommendations and are not present in the application.

## Status legend

| Marker | Meaning |
| --- | --- |
| **Implemented** | Component exists and is reachable in the SPA or admin. |
| **Partial** | Component exists but has known defects or limited variants. |
| **Proposed** | Recommended component; not implemented. |
| **Backend only** | Related capability exists in Django but no component surface found. |

---

## Component map

| Component | Status | Current source / proposed location | Notes |
| --- | --- | --- | --- |
| Button | Implemented | `components/Button.jsx`-style usage and CSS classes | Primary, secondary, danger, icon variants. |
| IconButton | Implemented | `components/Icon.jsx` + CSS | Icon-only actions; requires `aria-label`. |
| Input / Textarea / Select | Implemented | Forms across auth, profile, composer | Needs consistent error/retry patterns. |
| Checkbox / Switch | Implemented | Notification settings dialog | Switch uses `role="switch"`. |
| Avatar | Implemented | `components/UserAvatar.jsx` | Image with coloured initial fallback. |
| Badge | Implemented | Navbar unread counts, status pills | Needs consistent semantic variants. |
| Card | Implemented | Post/profile/rail/search cards | Standard surface pattern. |
| Dialog | Implemented | `ConfirmDialog.jsx`, story creator, viewer | Focus trap + restore. |
| Drawer | Implemented | `AppShell.jsx` mobile drawer | Focus trap, Escape/backdrop close. |
| MediaViewer | Implemented | `components/MediaViewer.jsx` | Zoom, prev/next, keyboard, failure state. |
| Skeleton | Implemented | Stories, posts, comments, notifications | Shimmer respects reduced motion. |
| EmptyState | Implemented | Most list pages | CTA should be consistent. |
| Tabs | Implemented | Friend requests, connections, profile proposals | ARIA tablist exists in requests. |
| Toast | Implemented admin / Proposed SPA | Admin toasts; SPA uses inline notices | Proposed shared SPA toast service. |
| Pagination | Partial | Home feed only | Proposed reusable component for all lists. |
| Composer | Implemented / Partial | `home.jsx`, `CreatePost.jsx` | Rich composer on home; simpler component elsewhere. |
| PostCard | Implemented | `home.jsx`, bookmarks, profile, post detail | Needs per-operation error state. |
| PostActions | Implemented | `components/PostActions.jsx` | Optimistic like, comments, bookmark, share. |
| CommentThread | Implemented | `PostActions.jsx` | Nested replies; needs collapse control proposal. |
| StoryCard / StoryStrip | Implemented | `components/Stories.jsx` | Avatar thumbnails; media preview proposed. |
| StoryViewer / StoryCreator | Implemented | `Stories.jsx` | Strong interaction model; reactions missing. |
| ConversationItem | Implemented | `Messages.jsx` | Two-pane list row. |
| MessageBubble | Implemented | `Messages.jsx` | Read receipts, attachment; edit/delete UI missing. |
| NotificationItem | Implemented | `Notifications.jsx` | Type icons, read state, deep links. |
| RailCard | Implemented | `AppShell.jsx` | Suggestions, requests, shortcuts. |
| KpiCard | Implemented admin | `config/admin_site.py` + admin templates | 12 real-data cards. |
| ChartCard | Implemented admin | Canvas charts | 7/30/90 analytics ranges. |
| DataTable | Implemented admin / Proposed SPA | Admin tables and standard lists | Responsive card fallback needed. |
| FileDropzone | Partial | Profile/composer/story upload controls | Needs consistent validation and retry. |
| SearchField | Partial | Navbar/sidebar/search page | Debounce/ref bug in user search. |
| ErrorBoundary | Proposed | — | Route-level graceful failure handling. |

---

## Primitive components

### Button

| Variant | Use |
| --- | --- |
| Primary | Publish, Save, Sign in, Accept, Send. |
| Secondary | Refresh, Cancel, Back, Follow when already following. |
| Ghost | Navbar icons, inline text actions. |
| Danger | Delete, Block, Reject with confirmation. |
| Busy | Any pending mutation. |

**Anatomy:** leading icon (optional), label, trailing icon (optional), loading spinner (busy).

**States:** default, hover, focus-visible, active, disabled, busy, error-adjacent, danger.

**Props:** `variant`, `size` (`sm|md|lg`), `icon`, `iconPosition`, `loading`, `disabled`, `type`, `onClick`, `ariaLabel`, `fullWidth`.

**Accessibility:** native `<button>`; busy label announced; icon-only buttons need `aria-label`; destructive actions require confirmation.

---

### IconButton

**Anatomy:** 40–44 px square container, 20 px icon, optional badge.

**States:** default, hover, selected, focus, disabled, busy.

**Props:** `icon`, `label`, `badge`, `active`, `tone`, `onClick`.

**Rules:**

- Never use an unlabelled icon button.
- Tooltip is supplementary, not the accessible name.
- Badge has text alternative such as `3 unread messages`.

---

### Input / Textarea / Select

**Anatomy:** label, required marker, control, help text, error text.

**States:** default, hover, focus, filled, disabled, invalid, busy.

**Props:** `id`, `label`, `value`, `placeholder`, `error`, `helpText`, `required`, `maxLength`, `autoComplete`.

**Accessibility:**

- `<label htmlFor>` required; fix current Register gaps.
- `aria-invalid` when error exists.
- Error uses `role="alert"`.
- Preserve user input on failure.

---

### Checkbox / Switch

**Use:** privacy flags, notification preferences, remember me.

**States:** unchecked, checked, indeterminate (checkbox only), disabled, focused.

**Accessibility:** native checkbox where possible; notification switches follow `role="switch"` + `aria-checked`.

---

### Avatar

**Sizes:** 24, 32, 40, 48, 64, 96 px.

**Variants:** image, initial fallback, online indicator, ring (story unseen), interactive (opens media/story).

**States:** loading, failed image, viewed vs unseen story ring.

**Props:** `user`, `size`, `ring`, `online`, `interactive`, `onClick`.

**Accessibility:** image avatar uses meaningful alt text; decorative fallback uses `aria-hidden` when adjacent to name.

---

### Badge

**Variants:** count, status, type, audience, trend.

**Colours:** primary (unread), teal (success/online), amber (pending), danger (error), slate (neutral).

**Rules:** count badges have accessible text; do not rely only on dot colour.

---

### Card

**Anatomy:** optional header, media, body, footer/actions.

**Variants:** post, profile, rail, search result, KPI, analytics, conversation.

**States:** default, hover (interactive only), loading skeleton, selected, error.

**Tokens:** 16–20 px radius, `--sc-shadow-sm`, `--sc-color-border`.

---

### Dialog / ConfirmDialog

**Anatomy:** overlay, panel, header, body, footer actions, close control.

**Variants:** confirmation, form, media, preferences, story creator.

**States:** open, busy, error, closing.

**Accessibility:**

- `role="dialog"` or `role="alertdialog"`.
- Focus trap, Escape close, backdrop close where safe.
- Restore focus to trigger.
- Destructive confirmations use explicit verb labels (`Delete post`, not `OK`).

---

### Drawer / BottomSheet

**Use:** mobile navigation, More menu, filter panels, proposed group settings.

**States:** open, closed, dragging (proposed), busy.

**Accessibility:** focus trap, body scroll lock, Escape/backdrop close, `aria-modal`.

---

### MediaViewer

**Existing:** close, previous/next, 50–400% zoom, fit, failed-media message, keyboard support, focus restoration.

**Proposed addition:** download/share action only where permissions allow.

**Accessibility:** announce current index (`1 of 4`), arrow keys, Escape, zoom controls with labels.

---

### Skeleton

**Variants:** text line, avatar, post card, story, comment, notification, KPI.

**Rules:** geometry matches loaded state; no layout shift; shimmer disabled under reduced motion.

---

### EmptyState

**Anatomy:** icon/illustration, title, one-sentence explanation, optional CTA.

**Examples:**

- No posts yet → `Share your first update`.
- No saved posts → `Browse feed`.
- No conversations → `Find people to message`.
- No notifications → `You're all caught up`.

---

### Tabs

**Variants:** underline (desktop content), segmented (mobile filters), pill (admin analytics range).

**States:** selected, unselected, disabled, busy, badge.

**Accessibility:** `role="tablist"`, `aria-selected`, arrow-key navigation; current FriendRequests implementation is a good reference.

---

### Pagination

**Status:** Proposed for general use; home feed has IntersectionObserver pagination only.

**Anatomy:** previous button, page indicators or `Load more`, next button, result summary.

**Variants:** numbered, load-more, infinite-scroll sentinel.

**Rules:**

- Consume `{count, next, previous, results}` where available.
- `page_size` alone does not paginate the feed; design must test with `page`.
- Show deterministic loading/error states and never duplicate pages.

---

### SearchField

**Anatomy:** search icon, input, clear button, optional keyboard shortcut, results count.

**States:** empty, typing, searching, results, no results, error, aborted.

**Rules:** debounce, abort stale request, allow retry after cancellation, sync URL in an effect (not render), maintain focus.

---

### FileDropzone

**Anatomy:** drop area, browse button, preview, filename/size, progress, remove control, error.

**Validation:**

| Upload | Current limit | Proposed display |
| --- | --- | --- |
| Avatar | 5 MB image | `PNG/JPG up to 5 MB`. |
| Cover | 10 MB image | `PNG/JPG up to 10 MB`. |
| Post image | 10 MB | `Images up to 10 MB`. |
| Post video | 100 MB | `Videos up to 100 MB`. |
| Story media | 25 MB | `Photos or short videos up to 25 MB`. |
| Chat attachment | 25 MB, allowed MIME prefixes | `Attachment up to 25 MB`. |

**States:** idle, hover, selected, uploading, success, invalid, retry.

---

## Feature components

### Composer

**Variants:** compact home composer, standalone create-post composer, proposed poll/schedule extensions.

**Anatomy:** avatar, trigger/textarea, media controls, audience selector, optional poll/schedule, publish button, progress.

**States:** collapsed, expanded, uploading, publishing, validation error, success.

**Rules:**

- Allow text or supported media; fix images-only edit validation.
- Audience options must reflect backend values observed in `PostSerializer`.
- Poll and schedule controls are proposed/backend-only until CRUD/publisher work exists.

---

### PostCard

**Anatomy:** author row, audience/time, menu, content, media gallery/video, action bar, comment composer.

**Variants:** feed, bookmark, profile, detail, repost context.

**States:** default, loading, media-failed, editing, deleting, reporting, pinned, reposted.

**Rules:**

- Per-post menu with owner actions (edit, pin/unpin, delete) and non-owner actions (repost, report).
- Per-operation error state; avoid shared global error leakage.
- Pinned badge is informational until ordering is implemented.
- Media gallery opens `MediaViewer`.

---

### PostActions

**Anatomy:** like, comment, share, repost, bookmark controls with counts.

**States:** default, active, busy, optimistic pending, rollback error.

**Rules:** like optimistic update with rollback; bookmark should also optimistic-update in proposed design; share uses Web Share API with clipboard fallback; report opens a form dialog.

---

### CommentThread

**Anatomy:** comment row, avatar, author, timestamp, body, reply/edit/delete controls, nested children.

**States:** collapsed, expanded, loading replies, editing, deleting, mention highlighted (proposed), reaction active (backend only).

**Rules:** indent 24 px per level with a cap; offer collapse for deep threads; preserve parent validation and cycle protection from backend.

---

### StoryCard / StoryStrip

**Anatomy:** avatar ring, author label, viewed/unviewed state, own-story add tile.

**States:** unseen, viewed, own, loading, empty.

**Rules:** own story first, then newest activity; horizontal scroll snap; media thumbnail preview proposed.

---

### StoryViewer

**Anatomy:** progress bars, author header, media stage, caption, navigation, pause, close, proposed reaction selector.

**States:** playing, paused, loading, video-ended, failed, reduced-motion manual.

**Rules:** 5-second auto-advance, keyboard arrows, Escape, pause only for non-video, record view once.

---

### ConversationItem

**Anatomy:** avatar, name, presence dot, last message, timestamp, unread badge, selection.

**States:** active, unread, read, online, offline, busy, search-match.

**Rules:** local search; unread counts; block-filtered list; proposed group badge when group UI exists.

---

### MessageBubble

**Anatomy:** bubble, sender/own alignment, text/attachment, timestamp, read receipt, menu.

**States:** sending, sent, delivered, read, failed, edited, deleted, attachment loading.

**Rules:** soft-deleted messages disappear; edit/delete controls are proposed UI for existing WS/REST events; attachment-only send must be enabled.

---

### NotificationItem

**Anatomy:** type icon, title, preview, timestamp, read/unread state, action link, mark-read control.

**States:** unread, read, busy, deep-link available, live-arrived.

**Rules:** seven implemented notification categories; mark read should update all clients in proposed WS design; busy state must not bypass read action.

---

### RailCard

**Variants:** suggestions, friend requests, friends, shortcuts, context help.

**States:** default, loading, empty, action busy.

**Rules:** right rail content should be context-aware in the proposed redesign but must not introduce unsupported `/explore` or `/settings` routes.

---

## Admin components

### KpiCard

**Existing 12 labels:** Total Users, Active Users, Total Posts, Total Comments, Pending Reports, Total Likes, New Registrations, Friend Requests, Total Stories, Active Stories, Expired Stories, Total Story Reactions.

**Anatomy:** label, value, description, icon tile, accent, trend chip.

**States:** real value, permission-masked `—`, unavailable relation, trend up/down/flat, loading.

**Rules:** permission-driven rendering; fix likes link; rename/describe Pending Reports until status workflow exists.

---

### ChartCard

**Anatomy:** title, range selector, legend, canvas chart, empty/error state.

**Variants:** line (registrations, active users, messages), bar (posts, comments, likes), combined engagement.

**Rules:** 7/30/90 day ranges; six-month monthly series; labels come from real aggregates; no invented data.

---

### DataTable

**Anatomy:** sticky header, rows, sort/filter controls, row actions, empty state.

**States:** loading, populated, empty, error, selected, busy action.

**Rules:** responsive cards below 760 px; destructive moderation actions require confirmation; table columns permission-aware.

---

## Component documentation template

Each future component entry should include:

1. Status and source reference.
2. Anatomy diagram or description.
3. Variants and sizes.
4. State matrix.
5. Props / API contract.
6. Keyboard interaction.
7. Screen-reader behaviour.
8. Responsive behaviour.
9. Example usage.
10. Acceptance criteria.

---

## Library acceptance criteria

- No feature component duplicates token values.
- Every interactive component has all states documented.
- Icon-only controls expose accessible names.
- Loading geometry matches loaded geometry.
- Form components expose field-level errors.
- Mobile variants use ≥44 px targets.
- Proposed components are clearly marked until implemented.
- Existing known defects (search loading, attachment-only send, shared errors) are tracked rather than silently adopted.

# 11 — Social Feed Design

## Purpose

This document specifies the social feed surface in detail: stories entry, composer, post card, actions, comments, moderation, pagination, and backend-only extensions.

## Existing implemented UI

The active feed is on `/`. It combines:

- `Stories.jsx` grouped strip and viewer.
- Home composer with text, image/video, audience, preview, progress, validation.
- `social/feed/` list with `?page=`, `page_size`, and IntersectionObserver sentinel.
- Post cards with author/time/audience, media gallery/video, pinned/repost indicators, menus.
- `PostActions.jsx`: optimistic likes, bookmarks, comments, threaded replies, edit/delete, share.
- Owner actions: edit, pin/unpin, delete.
- Non-owner actions: repost, report.
- `MediaViewer` for gallery images.

### Status markers

| Capability | Status |
| --- | --- |
| Text/image/video posts | Implemented. |
| Audience selection | Implemented. |
| Likes/bookmarks/comments/replies | Implemented. |
| Pagination via `page` | Implemented; opt-in. |
| Repost/pin/report | Partial. |
| Polls | Backend only / partial. |
| Scheduling | Backend only / partial. |
| Multi-image upload | Model exists; unreachable. |
| Hashtag browsing | Backend derived; no UI/endpoint. |
| Comment reactions | Backend only. |

---

## Proposed feed hierarchy

```text
HOME
  STORIES
  COMPOSER
  FEED
    POST CARD
      author row
      content / media
      action bar
      comment composer
      comment thread
    pagination
```

### Visual rhythm

| Element | Specification |
| --- | --- |
| Section header | 24 px H2 or 11 px eyebrow + 28 px H1. |
| Card padding | 20 px desktop; 16 px mobile. |
| Card radius | 20 px; shadow `sm`. |
| Card gap | 20 px. |
| Author row | 40 px avatar, 14 px name, 12 px metadata. |
| Content | 16/24 body; 8 px gap to media. |
| Media | 14 px radius, 16:9 max, max-height 520 px. |
| Action bar | 40 px controls, 8 px gaps, top border. |
| Comments | 8 px row gap, 24 px indent per level. |

---

## Composer design

### Existing behaviour

- Collapsed input prompting `Share an update`.
- Expanded textarea.
- Image/video selection with previews.
- Audience dropdown.
- Upload progress and validation: images ≤10 MB, videos ≤100 MB.
- Publish action with busy state.

### Proposed layout

```text
┌──────────────────────────────────────────────────────────────┐
│ [avatar] What's happening in your circle?                    │
│                                                              │
│ [image] [video] [audience: Public ▾] [poll*] [schedule*]      │
│                                                     [Publish] │
└──────────────────────────────────────────────────────────────┘
```

### Composer states

| State | Behaviour |
| --- | --- |
| Collapsed | Single-line trigger; media/audience controls visible but compact. |
| Expanded | Textarea auto-grows to 160 px then scrolls. |
| Media selected | Thumbnail/video preview, filename/size, remove control. |
| Uploading | Progress bar; controls disabled except Cancel/Remove where safe. |
| Validation error | Inline field error; preserve text/media. |
| Publishing | Button `Publishing…`; prevent duplicate submissions. |
| Success | Composer resets; notice; new post placed according to sort. |
| Auth changed | Proposed reactive hide/show; no stale render from localStorage. |

### Validation rules

- Content or supported media required.
- Image ≤10 MB; video ≤100 MB.
- Audience uses backend-supported values.
- Proposed images-only posts require serializer/upload reachable; current edit path rejects empty content when media only in `post.images`.

---

## Post card anatomy

```text
┌──────────────────────────────────────────────────────────────┐
│ [avatar] Name ✓  @handle · 18m  [Public] [Pinned] [Reposted] │
│                                                      [•••]  │
│ Post text with #hashtags                                     │
│ [media gallery / video]                                      │
│ ─────────────────────────────────────────────────────────── │
│ ♥ 24      💬 8      ↻ 3         [Share] [Save]               │
│ ─────────────────────────────────────────────────────────── │
│ [avatar] Write a comment...                        [Post]    │
│ [comment][reply][comment]                                    │
└──────────────────────────────────────────────────────────────┘
```

### Header rules

- Avatar opens media viewer when interactive.
- Name links to `/users/:id`; timestamp links to `/posts/:id`.
- Audience badge uses neutral pill; verified badge uses blue icon + tooltip.
- Pinned badge is informational until ordering is implemented.
- Repost indicator uses repost icon + label.

### Menu rules

| Owner | Non-owner |
| --- | --- |
| Edit post | Repost |
| Pin / Unpin | Report post |
| Delete post | — |

Menus close on outside click, Escape, and action selection. Destructive actions use `ConfirmDialog`.

---

## Post actions

| Action | Existing behaviour | Proposed refinement |
| --- | --- | --- |
| Like | Optimistic update with rollback; notification produced. | Keep; announce count via live region. |
| Comment | Lazy-loaded thread; inline composer. | Add collapse for deep threads. |
| Bookmark | Toggle endpoint; no optimistic UI. | Optimistic update with rollback. |
| Share | Web Share API or clipboard; notice auto-dismiss. | Persistent accessible status. |
| Repost | Toggle endpoint; idempotent; own posts rejected. | Notify sender in backend proposal; no false success on failure. |
| Pin | Toggle endpoint; no ordering effect. | Apply pin-first ordering or rename badge. |
| Report | Form submission; no moderation workflow. | Per-post busy state; add status workflow backend. |
| Edit | Owner-only; media-only caveat. | Include `post.images` and `video` in media-presence check. |
| Delete | Owner-only confirmation. | Preserve per-card busy state. |

---

## Comments and mentions

### Existing behaviour

- Comments grouped by parent, with cycle protection.
- Reply, edit, delete with confirmations.
- Mentions typed as `@username`; backend creates mention records and notifications.
- Lazy loading on first expansion.

### Proposed refinements

| ID | Refinement | Status |
| --- | --- | --- |
| C-01 | Mention picker with username suggestions. | Proposed. |
| C-02 | Strip trailing punctuation from mention regex. | Proposed bug fix. |
| C-03 | Collapse deep threads after 3 levels. | Proposed. |
| C-04 | Reaction picker for comments. | Backend only / proposed UI. |
| C-05 | Pagination/load more for comments. | Proposed; backend currently unpaginated. |
| C-06 | Distinguish reply-to label from nested indent. | Proposed. |
| C-07 | Show comment policy explanation when comments disabled. | Proposed. |

---

## Media gallery

- Images from `post.images` render in a gallery; current serializer field is read-only.
- Single `image` and `video` fields remain the reachable upload paths.
- Media tile opens `MediaViewer` with index, zoom, arrow keys, Escape.
- Failed media shows neutral placeholder with accessible text.
- Proposed multi-image upload requires writable API support.

---

## Pagination and sorting

### Existing contract

- Feed endpoint returns a bare array without `page`.
- With `?page=1`, it returns `{count, next, previous, results}`.
- Default page size 10, max 50; `page_size` alone does not paginate.
- Home uses IntersectionObserver sentinel.

### Proposed UI

```text
[loaded posts]
[ sentinel / skeleton while next page loads ]
[ Load more ]  ← fallback if observer unsupported/fails
Showing 20 of 84
```

Rules:

- Always request with `page`.
- Prevent duplicate in-flight requests.
- On error, show retry without losing loaded posts.
- Use `count` for summary when pagination is active.
- Do not imply sort control works unless backend supports it; current `Newest first` is a label.

---

## Backend-only feed extensions

| Capability | Backend evidence | UI proposal | Must not claim |
| --- | --- | --- | --- |
| Polls | `Poll`, `PollOption`, `PollVote`, vote endpoint. | Poll card with options, single active vote, results. | Poll create/edit/list until endpoints exist. |
| Scheduling | `scheduled_for` field and visibility filter. | Date-time picker in composer. | Automatic publishing until job exists. |
| Drafts | `is_draft`, `?drafts=true`. | Drafts view with edit/publish. | Correct draft-only filter until backend fixed. |
| Hashtags | Derived from content. | Clickable hashtag chips and browse page. | Browse endpoint/page; neither exists. |
| Multi-image | `PostImage` model, read-only serializer. | Multi-file uploader + gallery builder. | Reachable upload until API writer exists. |
| Report moderation | Create-only report endpoint. | Admin status/reject/resolve. | Resolve endpoint/status field. |

---

## Feed states

| State | UI |
| --- | --- |
| Loading | Story skeleton, composer skeleton, two post skeletons. |
| Empty | Explanation + `Find people` / `Create a post`. |
| Error | Inline error card with retry; composer preserved. |
| Refreshing | Subtle progress; current posts remain. |
| Pagination loading | Sentinel skeleton. |
| Pagination error | Load-more retry. |
| Media failure | Placeholder tile; other media still usable. |
| Blocked/private target | Neutral unavailable state; no private detail leakage. |

---

## Accessibility requirements

- Feed is a labelled `<main>` region.
- Each post is an `<article>` with accessible heading/label.
- Action counts are text, not colour-only icons.
- Comment expansion uses `aria-expanded`.
- Menus use `aria-haspopup` and keyboard navigation.
- Dialogs trap focus and restore.
- Live regions announce like/bookmark/save and pagination results politely.
- Reduced motion disables skeleton shimmer and hover lift.

---

## Acceptance criteria

- Composer supports text, image/video, audience, progress, and validation.
- Post card renders all implemented indicators and actions.
- Owner/non-owner menus are permission-correct.
- Comments support reply, edit, delete, mention, and expansion states.
- Feed pagination requires `page` and handles `next`.
- Backend-only features are clearly labelled in design review.
- All loading/empty/error states are implemented.
- Keyboard and screen-reader behaviour verified on desktop and mobile.

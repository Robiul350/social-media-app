# 10 — Dashboard Design

## Scope clarification

SocialConnect has two distinct “dashboard” surfaces:

| Surface | Where | Purpose | Status |
| --- | --- | --- | --- |
| **SPA home dashboard** | `/` in React app | Daily user landing page: stories, composer, feed, social shortcuts. | Implemented. |
| **Admin dashboard** | `/admin/` in Django custom admin | Staff metrics, charts, moderation, roles, system status. | Implemented; browser verification historical. |

This document covers the **SPA home dashboard**. See `16-ADMIN_PANEL_DESIGN.md` for the admin dashboard.

---

## Existing implemented UI

The home page renders:

1. Section heading `YOUR COMMUNITY` with refresh control.
2. Stories strip with own story first and unseen rings.
3. Composer supporting text, image/video, audience selection, preview, and publish.
4. Feed from `social/feed/?page=1` with IntersectionObserver pagination.
5. Post cards with author links, audience badges, media, actions, comments, menus, share/report/repost/pin actions.
6. Right rail on desktop with suggested people, incoming friend requests, friends, and shortcuts.

### Existing strengths

- Single scroll surface for the primary daily task.
- Strong empty/loading states and notices.
- Right rail makes discovery and requests visible without extra navigation.
- Refresh preserves already-loaded pages.

### Existing caveats

- Initial feed request has no abort controller.
- `loggedIn` is derived during render and does not react to auth-change events.
- Shared error state can leak between edit, delete, share, report, repost, and pin flows.
- Editing rejects empty text when media exists only in `post.images`.
- Pinned badge has no ordering effect.
- Most list pages outside home do not paginate.

---

## Proposed redesigned SPA dashboard

### Information priority

| Priority | Region | Why |
| --- | --- | --- |
| 1 | Composer | Fastest path to user action. |
| 2 | Stories | Time-sensitive, 24-hour content. |
| 3 | Feed | Main consumption surface. |
| 4 | Right rail | Secondary discovery and requests. |

```text
┌────────────────────────────────────────────────────────────────────────┐
| Home                                            Newest first ▾ [Refresh]|
├────────────────────────────────────────────────────────────────────────┤
| STORIES                                                       See all   |
| [+You][Ava][Noah][Mia][Leo][Iris][Omar][Zoe]                            |
├────────────────────────────────────────────────────────────────────────┤
| [avatar] What's happening in your circle?                              |
| [Media] [Audience: Public ▾] [Poll*] [Schedule*]            [Publish]  |
├────────────────────────────────────────────────────────────────────────┤
| FEED                                                                   |
| [Post card]                                                            |
| [Post card]                                                            |
| [Loading sentinel / Load more]                                         |
└────────────────────────────────────────────────────────────────────────┘
```

`Poll*` and `Schedule*` are proposed controls for backend-only/partial features.

---

## Desktop layout specification

| Region | Size / rule |
| --- | --- |
| Page header | 72 px top area including eyebrow, H1, sort, refresh. |
| Stories card | Full content width, 20 px padding, 100 px story items. |
| Composer card | 20 px padding, 16 px avatar, 48 px collapsed input. |
| Feed column | 780 px max. |
| Card gap | 20 px. |
| Right rail | 312 px, sticky below header, cards separated by 20 px. |
| Section eyebrow | 11 px uppercase, muted. |
| H1 | 28/36 display bold. |

### Right rail cards

| Card | Data source | Current status | Proposed treatment |
| --- | --- | --- | --- |
| Suggested people | `users/search/?suggested=true` | Implemented. | Three rows with Follow; `See more` → `/search`. |
| Friend requests | `social/friend-requests/` | Implemented. | Incoming count + Accept/Reject shortcut. |
| Friends | `social/friends/` | Implemented. | Avatar row + `See all` → `/connections/friends`. |
| Shortcuts | Static links | Implemented. | Saved posts, profile, settings dialog, admin where permitted. |
| Trending hashtags | Derived hashtags only | Backend only / Not Found endpoint. | **Proposed only**; do not add until endpoint exists. |

---

## Mobile layout specification

```text
┌──────────────────────────────┐
│ HOME              [⌕] [↻]   │
├──────────────────────────────┤
| STORIES                      |
| + [You][Ava][Noah][Mia][›]   |
├──────────────────────────────┤
| [av] What's new with you?    |
| [media][audience ▾] [Publish]|
├──────────────────────────────┤
| [Post card]                  |
| [Post card]                  |
└──────────────────────────────┘
```

| Rule | Specification |
| --- | --- |
| Side gutters | 16 px at ≤560 px; 12 px at ≤400 px. |
| Stories | Edge-to-edge scroll with 12 px snap padding. |
| Composer | Two rows; expand on focus; Publish remains reachable. |
| Feed | One card per scroll focus; media max 52vh. |
| Bottom nav | 64 px plus safe area; content bottom padding 88 px. |
| Rail | Hidden; cards reachable via dedicated pages/drawer. |

---

## Dashboard states

| State | Treatment |
| --- | --- |
| First load | Skeleton stories, composer, and two post placeholders. |
| Feed empty | `Your feed is quiet right now.` CTA: `Find people` and `Create a post`. |
| Stories empty | `No stories yet.` CTA: `Share your first story`. |
| Feed error | Inline error card with `Try again`; preserve composer content. |
| Refresh | Non-blocking progress indicator; keep existing posts visible. |
| Pagination loading | Sentinel skeleton; prevent duplicate page requests. |
| Pagination error | `Load more` retry button; previously loaded posts remain. |
| Auth change | Composer/stories react to `socialconnect:auth-change` in proposed design. |
| Offline | Neutral status notice; retry when connection returns. |

---

## Interaction rules

| Action | Behaviour |
| --- | --- |
| Refresh | Reload first page and reconcile with loaded pages; do not clear composer. |
| Newest first | Current label is static in source; proposed control requires backend/API sort support or must remain informational. |
| Publish | Disable while busy; show `Publishing…`; replace composer content on success. |
| Media select | Preview with remove; show upload progress; validate before submit. |
| Audience | Use backend-supported values; persist selection during upload. |
| Story open | Record view once; open viewer modal with progress bars. |
| Post menu | Owner: edit, pin/unpin, delete. Non-owner: repost, report. |
| Deep link | Author → profile; post text/time → detail; comments expand inline or detail. |
| Pagination | Use `?page=` because bare feed is unpaginated by design/test. |

---

## Proposed dashboard improvements

| ID | Improvement | Status |
| --- | --- | --- |
| D-01 | Per-operation error state instead of one shared `error`. | Proposed. |
| D-02 | Abort initial feed request on unmount/navigation. | Proposed. |
| D-03 | React to auth changes for composer/stories visibility. | Proposed. |
| D-04 | Allow media-only post edits by including `post.images`. | Proposed fix. |
| D-05 | Per-post report busy state. | Proposed fix. |
| D-06 | Put pinned posts first where badge is shown. | Proposed; requires ordering change. |
| D-07 | Context-aware rail per route. | Proposed. |
| D-08 | Add poll/schedule composer controls only after backend completion. | Backend-only / Proposed. |
| D-09 | Add skip link and consistent validation summary. | Proposed. |
| D-10 | Add pagination summary (`Showing 20 of 84`) where `count` exists. | Proposed. |

---

## Accessibility requirements

- H1 is `Home` or `Your community`; section headings use H2.
- Stories strip is a labelled region with scrollable list semantics.
- Composer fields have visible labels or accessible names.
- Media buttons expose type and file name.
- Refresh announces completion with `role="status"`.
- Feed updates announce new count politely.
- Skeleton regions are `aria-hidden` while loading; a status message announces loading.
- Focus returns to trigger after dialogs close.
- Reduced motion disables shimmer and transitions.

---

## Acceptance criteria

- Dashboard layout matches 780 px centred desktop and full-width mobile.
- Right rail appears at ≥1280 px and is hidden at ≤1180 px.
- Composer supports all currently implemented fields and validation.
- Feed pagination works only with `page`, matching backend contract.
- All six states are implemented: loading, empty, error, refresh, pagination, offline.
- No proposed-only control appears in current-behaviour handoff.
- Auth changes immediately update composer/story visibility in proposed implementation.
- Keyboard and screen-reader checks pass for stories, composer, and feed actions.

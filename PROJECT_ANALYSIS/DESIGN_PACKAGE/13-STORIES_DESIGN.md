# 13 — Stories Design

## Purpose

This document specifies the stories strip, creation flow, viewer, privacy, expiry, reactions proposal, and all interaction states.

## Existing implemented UI

The current `Stories.jsx` implementation is a strong interaction surface:

- Grouped strip with own story first, then newest activity.
- Unseen rings and viewed ID tracking in component state.
- Creation dialog with image/video validation up to 25 MB, caption up to 500 characters, privacy selection, and upload progress.
- Viewer modal with progress bars, 5-second auto-advance, pause for non-video, close, previous/next, keyboard navigation, reduced-motion accommodation, and video end handling.
- View recording via `POST /api/users/stories/<pk>/view/`.
- Backend has seven story reaction types, a reaction list endpoint, and a `story_reactions` notification preference.

### Current limitations

- No reaction UI despite backend endpoints.
- Viewed IDs are component-local and reset on remount.
- Viewer uses avatar-only thumbnails rather than story media previews.
- No story edit/delete endpoint or UI.
- Updating a reaction emits duplicate notifications.
- Root README wording that stories are “not integrated” is stale; source has a real Stories component.

---

## Information architecture

```text
Home / Stories entry
  ├── Strip
  │    ├── Own story tile
  │    └── Grouped author tiles
  ├── Creator dialog
  │    ├── Media selection
  │    ├── Caption
  │    ├── Privacy
  │    └── Upload progress
  └── Viewer modal
       ├── Progress bars
       ├── Author header
       ├── Media stage
       ├── Caption
       ├── Navigation controls
       ├── View recording
       └── Proposed reaction selector
```

---

## Stories strip

### Existing behaviour

- Horizontal strip on home.
- Own story first.
- Unseen ring emphasised.
- Click opens viewer grouped by author.

### Proposed design

```text
STORIES                                                    See all*
┌────────┬────────┬────────┬────────┬────────┬────────┐
│ +      │ [av]   │ [av]   │ [av]   │ [av]   │ [av]   │
│ You    │ Ava    │ Noah   │ Mia    │ Leo    │ Iris   │
│ Create │ 2h     │ 5h     │ 8h     │ 12h    │ 1d     │
└────────┴────────┴────────┴────────┴────────┴────────┘
```

`See all*` is proposed only if a dedicated stories page is added; currently stories appear on home.

| Element | Desktop | Mobile |
| --- | --- | --- |
| Item width | 100 px | 84 px |
| Avatar | 64 px | 56 px |
| Ring | 3 px gradient | 3 px gradient |
| Label | 12 px caption | 11–12 px caption |
| Scroll | Hidden scrollbar with arrow controls | Edge-to-edge snap scroll |
| Gap | 12 px | 10 px |

### Ring states

| State | Visual |
| --- | --- |
| Unseen | Blue/violet gradient ring, 3 px. |
| Viewed | Slate border, 1–2 px, reduced opacity. |
| Own with story | Teal ring plus small `+` or `You` label. |
| Own without story | Dashed neutral ring with plus icon. |
| Loading | Avatar skeleton with ring placeholder. |

---

## Story creator

### Existing behaviour

- Media selection: image or video.
- Max size 25 MB.
- Caption max 500 characters.
- Privacy options: `public | followers | friends`.
- Upload progress.
- Server sets author and 24-hour expiry.

### Proposed layout

```text
┌──────────────────────────────────────────┐
│ Create story                       [×]   │
├──────────────────────────────────────────┤
│ ┌──────────────────────────────────────┐ │
│ │ media preview / upload placeholder   │ │
│ └──────────────────────────────────────┘ │
│ [Change media] [Remove]                  │
│ Caption [..............................] │
│ 0/500                                    │
│ Who can see this story [Friends ▾]       │
│ [ ] Also share as post*                  │
│                                          │
│ [ Progress bar while uploading ]         │
│                              [Share]     │
└──────────────────────────────────────────┘
```

`Also share as post*` is proposed and would require new backend/UI work; do not present as current.

### Creator states

| State | Behaviour |
| --- | --- |
| Empty | Dropzone + browse button; Share disabled. |
| Media selected | Preview, filename/size, remove control. |
| Invalid type/size | Inline error; Share disabled. |
| Uploading | Progress bar; controls disabled except Cancel if supported. |
| Ready | Share enabled; caption/privacy editable. |
| Publishing | Busy label `Sharing…`; prevent duplicate submit. |
| Success | Close dialog, refresh strip, show own story ring. |
| Error | Retry with media/caption preserved. |
| Caption limit | Counter changes to danger near 500; hard max at 500. |

### Validation

| Field | Rule |
| --- | --- |
| Media | Required; image or video; ≤25 MB. |
| Caption | Optional; max 500 characters. |
| Privacy | One of backend-supported values. |
| Expiry | Server-controlled 24 hours; no client override. |

---

## Story viewer

### Existing behaviour

- Full-screen modal.
- Progress bars per item.
- 5-second auto-advance for non-video.
- Pause/resume for non-video.
- Video end handling.
- Previous/next controls and keyboard navigation.
- Escape close and focus restoration.
- Reduced motion disables auto-advance.
- View recorded when story is visible.

### Proposed layout

```text
┌──────────────────────────────────────────────────────────────┐
│ ████████░░  █████░░░░░  ███░░░░░░░                        │
│ [avatar] Ava Thompson · 2h        [Pause] [Close]            │
│                                                              │
│                    media stage                               │
│                    9:16 / 78vh max                           │
│                                                              │
│ caption text                                                 │
│                                                              │
│ [Previous]                             [Next]                │
│ reactions: [♥] [😂] [😮] [😢] [😡] [👏] [🔥]*             │
└──────────────────────────────────────────────────────────────┘
```

`reactions` are **proposed UI** for existing backend endpoints.

### Viewer specification

| Element | Specification |
| --- | --- |
| Backdrop | `#020617` at 92% opacity, 8 px blur. |
| Progress bars | 3 px height, 4 px gap, top 12 px, rounded. |
| Header | 56 px; avatar 36 px; white text; icon controls 36 px. |
| Media stage | Max width 480 px, max height 78vh, 16 px radius. |
| Caption | 15/22 white, max 3 lines with fade clamp. |
| Nav controls | 44 px circles, 32 px from side, semi-transparent surface. |
| Reaction row | **Proposed** 44 px chips, horizontally scrollable on mobile. |
| Counter | Proposed `12 reactions` with detail sheet. |

### Viewer states

| State | Behaviour |
| --- | --- |
| Loading | Spinner over neutral stage; progress paused. |
| Playing | Timer advances; progress bar fills. |
| Paused | Timer stops; Pause icon becomes Play for non-video. |
| Video playing | Native controls or custom play/pause; timer tied to video duration. |
| Video ended | Advance to next story. |
| Last story | Close viewer or return to first author group; choose one consistent rule. |
| Failed media | Neutral placeholder with `Story media unavailable`. |
| Reduced motion | No auto-advance; manual controls only. |
| Private/blocked | Viewer does not open; neutral unavailable state. |

---

## Reaction proposal

### Backend facts

- `POST /api/users/stories/<pk>/react/` with `reaction_type`.
- Seven reaction types are supported.
- `DELETE /api/users/stories/<pk>/react/` removes reaction.
- `GET /api/users/stories/<pk>/reactions/` returns total, counts by type, user reaction, list.
- `story_reactions` notification preference exists.
- Updating a reaction currently emits another notification.

### Proposed UI

```text
┌──────────────────────────────────────────┐
│ React to Ava's story                     │
│ [♥ Like] [😂 Haha] [😮 Wow] [😢 Sad]     │
│ [😡 Angry] [👏 Clap] [🔥 Fire]           │
│ You reacted: 🔥        [Remove reaction] │
│ 12 reactions · View list                 │
└──────────────────────────────────────────┘
```

| Rule | Specification |
| --- | --- |
| Selection | Tap once to set; tap same reaction again to remove. |
| Counts | Optimistic update with rollback. |
| Notification | Only on first reaction until duplicate-notification bug is fixed. |
| Preference | Respect `story_reactions` setting; hide or explain opt-out. |
| Accessibility | Each reaction is a labelled button; not emoji-only for screen readers. |

---

## Privacy and visibility

| Privacy value | Who can view |
| --- | --- |
| `public` | Any authenticated, non-blocked user. |
| `followers` | Approved followers only. |
| `friends` | Accepted friends only. |

Additional backend rules:

- Private profile gating.
- Block filtering.
- 24-hour expiry.
- Story must be visible for view/react/reactions endpoints.

Design rules:

- Do not show expired stories.
- Do not reveal author details for blocked/private-invisible stories.
- Show a neutral `Story unavailable` state when a deep link fails.

---

## Viewed state persistence

**Existing:** component-local state resets on remount.

**Proposed options:**

1. Persist viewed IDs in a session-scoped store keyed by story ID.
2. Reconcile with `StoryView` data if a future endpoint exposes viewed state.
3. Clear viewed IDs when the 24-hour expiry passes.

Acceptance: viewed ring stays viewed across route changes within the same session, but a fresh login or new day may reset according to product decision.

---

## Accessibility requirements

- Viewer is `role="dialog"` with `aria-modal`.
- Progress bars expose timing via accessible text; do not rely on visual animation.
- Pause/Play, Close, Previous, Next have visible labels or `sr-only` text.
- Arrow keys navigate; Escape closes.
- Focus is trapped and restored.
- Caption changes announced politely.
- Reduced motion disables auto-advance and decorative transitions.
- Reaction buttons have text labels, not only emoji.
- Creator dialog follows form error and upload progress patterns.

---

## Acceptance criteria

- Strip shows own story first and grouped authors with accurate unseen/viewed states.
- Creator enforces media size/type, caption limit, privacy, and upload progress.
- Viewer supports progress, pause, navigation, keyboard, video end, and reduced motion.
- View is recorded once per visible story.
- Backend-only reactions are labelled in current-behaviour material.
- Proposed reaction selector respects preferences and avoids duplicate notifications.
- All states above are implemented, including failed media and unavailable story.

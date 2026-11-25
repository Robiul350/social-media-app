# 12 — Profile Design

## Purpose

This document specifies own and public profile screens, edit profile, relationship states, privacy states, media, and stats.

## Existing implemented UI

`UserProfile.jsx` is the active profile screen. `Profile.jsx` exists but is unrouted/dead code and must not be used as the design basis.

### Current profile elements

- Cover image or `No cover photo`.
- Avatar.
- Display name, username, bio, location, website.
- Own profile: Edit profile.
- Other profile: Add friend / Follow / Message / Block actions depending on state.
- Stats: posts, followers, following.
- Authored posts list.
- Media viewer for cover/avatar.
- Confirmation dialogs for relationship and destructive actions.

### Current backend states

- `PublicProfileSerializer` exposes counts, follow state, friendship status, `can_view_profile`, `can_message`, `is_blocked`.
- Private profiles mask profile details and set `can_view_profile:false`.
- Blocked users receive 404.
- `posts_count` includes drafts/scheduled/non-public posts, which can disagree with visible posts.
- Mutual friends endpoint exists but has no SPA UI.

---

## Proposed own profile

```text
┌────────────────────────────────────────────────────────────────────────┐
│ [cover image — 240px desktop / 160px mobile, bottom scrim]            │
│                    [avatar 96px / 80px]                               │
│                    Ava Thompson  ✓  @ava                              │
│                    Product designer · Building calmer communities     │
│                    📍 London   🔗 ava.design   🗓 Joined Mar 2025      │
│                                                                      │
│                    [Edit profile] [Share profile]                     │
│                    [ 42 posts ][ 1.2k followers ][ 318 following ]    │
├────────────────────────────────────────────────────────────────────────┤
│ [ Posts ] [ Media ] [ About ]*                                        │
│ [post card] [post card] [post card]                                   │
└────────────────────────────────────────────────────────────────────────┘
```

`Media` and `About` are proposed derived views; no new backend endpoint is required.

### Layout specification

| Element | Desktop | Mobile |
| --- | --- | --- |
| Cover height | 240 px | 160 px |
| Avatar | 96 px, 4 px app-colour ring | 80 px, 3 px ring |
| Identity block | Centered, 16 px gap to actions | Centered, 12 px gap |
| Name | H3/H2 20–24 px semibold | H3 18–20 px |
| Metadata | Caption 12 px with icons | Caption 11–12 px, wraps |
| Actions | 40 px height | 44 px height, two rows |
| Stats | 3 equal cells, 1 px dividers | 3 equal cells |
| Tabs | 44 px underline | Full-width segmented |

---

## Proposed public profile

```text
┌────────────────────────────────────────────────────────────────────────┐
│ [cover]                                                                │
│             [avatar] Noah Williams @noah                               │
│             Bio · location · website                                   │
│             [Message] [Follow] [Add friend] [•••]                      │
│             [ 88 posts ][ 640 followers ][ 291 following ]             │
│             Mutual friends: Ava, Mia, Leo*                             │
├────────────────────────────────────────────────────────────────────────┤
│ [ Posts ] [ Media ] [ About ]*                                        │
└────────────────────────────────────────────────────────────────────────┘
```

`Mutual friends` uses the existing endpoint and is proposed UI.

### Relationship action matrix

| State | Primary action | Secondary action | Notes |
| --- | --- | --- | --- |
| Not following, no request | Follow | Add friend | Message if `can_message`. |
| Following | Following (toggle) | Add friend | Visual selected state. |
| Incoming request | Confirm request | Decline | Link to friend requests. |
| Outgoing request | Request sent | Cancel request | Use real `friend_request_id`; guard missing ID. |
| Friends | Friends / Unfriend | Message | Confirmation for unfriend. |
| `can_message=false` | Disabled Message | Explanation on hover/tap | Proposed improvement. |
| Blocked | Unblock from profile or list | — | Blocked profile normally 404. |

---

## Privacy states

| State | Display |
| --- | --- |
| Public profile | Full profile details and posts. |
| Private profile, allowed viewer | Full details; badge `Private profile` maybe shown. |
| Private profile, not allowed | Masked identity metadata; `can_view_profile:false`; no private details. |
| Blocked viewer | Neutral `Profile unavailable`; never reveal private data. |
| Deactivated user | Proposed neutral unavailable state. |

Rules:

- Do not use public post metadata to infer private details.
- Keep existing backend masking behaviour; design must not leak through preview cards.
- `can_message` and `can_view_profile` must drive UI, not client guesses.

---

## Edit profile design

### Existing behaviour

`EditProfile.jsx` edits:

- First name, last name, username-derived identity.
- Bio, location, website.
- Profile picture and cover photo with previews/removal flags.
- Private profile flag.
- Who can comment policy.
- Who can message policy.
- Social/education/work fields where present in serializer.

### Proposed layout

```text
┌────────────────────────────────────────────────────────────────────────┐
│ [<] Edit profile                                          [Cancel]*   │
├────────────────────────────────────────────────────────────────────────┤
│ PROFILE MEDIA                  ACCOUNT DETAILS                         │
│ [avatar preview] [Change]      First name [______] Last [______]      │
│ [cover preview]  [Change]      Bio [...............................] │
│ [Remove avatar]                Location [______] Website [______]     │
│                                Social / work / education fields       │
├────────────────────────────────────────────────────────────────────────┤
│ VISIBILITY & PERMISSIONS                                               │
│ [ ] Private profile                                                    │
│ Who can comment [Everyone ▾]   Who can message [Everyone ▾]            │
│                                                        [Save changes]  │
└────────────────────────────────────────────────────────────────────────┘
```

`Cancel` is proposed; current screen lacks a back/cancel control.

### Form rules

| Rule | Specification |
| --- | --- |
| Labels | Explicit `htmlFor` and IDs. |
| Errors | Field-level and form-level with `role="alert"`. |
| File validation | Avatar ≤5 MB; cover ≤10 MB; images only. |
| Invalid file | Disable submit until removed; proposed fix. |
| Save | Busy label `Saving…`; prevent duplicate submissions. |
| Success | Dispatch auth/profile refresh event; return to profile. |
| Load failure | Retry button, not manual reload instruction. |
| Unsaved changes | Proposed confirmation before leaving. |
| Abort | Proposed AbortController on profile GET. |

---

## Stats design

| Stat | Current source | Proposed display |
| --- | --- | --- |
| Posts | `posts_count` | Label `Posts`; tooltip `Authored posts` until count is corrected. |
| Followers | followers count. | Click → `/connections/followers`. |
| Following | following count. | Click → `/connections/following`. |

Proposal: align `posts_count` with visible posts or rename the label once backend is updated. Do not silently change the number in UI without backend agreement.

---

## Profile states

| State | Treatment |
| --- | --- |
| Loading | Cover/avatar skeleton, identity lines, stat skeleton, post skeletons. |
| Error | Retry card; preserve last known profile if available. |
| Cover failed | Placeholder shown; reset failure when profile/user changes. |
| Empty posts | `No posts yet.` Own profile CTA: `Create a post`; public profile: no CTA. |
| Private restricted | Masked identity card and explanation. |
| Blocked | Neutral unavailable state. |
| Relationship busy | Button busy label; disable related actions. |
| Friend ID missing | Disable friend action; proposed guard. |

---

## Media and tabs

### Posts tab

- Existing authored posts list.
- Use `PostCard` with owner/non-owner menu rules.
- Add pagination proposal because current profile posts are unpaginated.

### Media tab — proposed

- Grid of posts with image/video.
- Uses existing post data; no new endpoint.
- Media tiles open `MediaViewer` or post detail.

### About tab — proposed

- Bio, location, website, joined date, work/education/social fields.
- Only shows fields allowed by current serializer/privacy.

---

## Accessibility requirements

- Profile header is a labelled region with H1/H2 name.
- Avatar/cover viewer controls have accessible names and focus restore.
- Relationship buttons expose state (`aria-pressed` where appropriate).
- Disabled message action includes visible explanation, not only tooltip.
- Stats are links or buttons with meaningful labels.
- Form errors are associated with fields.
- Media tabs use tablist semantics.
- Confirmation dialogs use `alertdialog`.

---

## Acceptance criteria

- Active profile implementation is `UserProfile.jsx`; dead `Profile.jsx` is excluded from handoff.
- Own and public profiles render correct action sets from backend state.
- Private and blocked states reveal no protected data.
- Edit profile supports all implemented fields and uploads.
- Load failure offers retry; invalid file blocks submit.
- Stats link to correct connection pages.
- Proposed tabs/features are labelled as proposals.
- Layout meets desktop/mobile specifications and accessibility requirements.

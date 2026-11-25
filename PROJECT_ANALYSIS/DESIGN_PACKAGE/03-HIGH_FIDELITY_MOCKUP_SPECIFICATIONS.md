# 03 — High-Fidelity Mockup Specifications

## Preview status

An actual image-generation preview was attempted, but the image service returned an invalid-credential error. No image assets were created. This document therefore supplies the detailed, implementation-ready visual specifications that would accompany a high-fidelity mockup set.

The specifications below are **proposed redesign** directions. They preserve current information architecture and real features but refine hierarchy, spacing, and consistency. Current behaviour is listed first in each section so the two states are never confused.

## Specification conventions

| Property | Meaning |
| --- | --- |
| **Existing implemented UI** | Behaviour and structure observed in current source. |
| **Proposed redesigned UI** | Recommended visual direction; not implemented. |
| **Backend-only / Proposed surface** | Capability exists in Django but has no current SPA surface, or a UI idea that needs backend work. |
| **px values** | CSS pixels at a 1440 × 900 desktop baseline and 390 × 844 mobile baseline. |
| **Tokens** | Reference names in `04-DESIGN_SYSTEM.md`, `05-COLOR_PALETTE.md`, and `06-TYPOGRAPHY_SYSTEM.md`. |

---

## 1. Global desktop shell

### Existing implemented UI

- Sticky top navbar, approximately 72 px high.
- Three columns: left sidebar, main `<Outlet />`, right rail.
- Brand mark is a square `S`; full wordmark is `SocialConnect`.
- Navigation includes Home, Explore, Friends, Messages, Alerts, search, theme toggle, settings dialog, and account menu.
- Right rail is fully populated only on `/`; other routes use generic discovery/shortcut cards.

### Proposed redesigned UI

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ 72px header: [SC] brand | primary nav | search | icons | theme | avatar      │
├────────────────┬──────────────────────────────────────────────┬──────────────┤
│ sidebar 264px  │ content column max 780px                     │ rail 312px   │
│ profile card   │ 24px section gap, 20px card gap              │ context card │
│ grouped nav    │                                              │ context card │
└────────────────┴──────────────────────────────────────────────┴──────────────┘
```

| Element | Proposed specification |
| --- | --- |
| Canvas | `--sc-surface-app` `#F8FAFC`; subtle top gradient from transparent to blue-tinted at 4% opacity. |
| Header | 72 px, sticky, `--sc-surface-raised` with 1 px `--sc-border`, blur 12 px at 88% opacity. |
| Brand lockup | 36 × 36 px rounded-square gradient mark; wordmark 18 px display semibold. |
| Nav item height | 44 px; 12 px horizontal padding; active state blue surface and 2 px left indicator. |
| Sidebar | 264 px fixed; 24 px top padding; grouped sections with 11 px uppercase labels. |
| Content | 780 px max; centered; 32 px top padding; 20 px vertical card gaps. |
| Rail | 312 px; 16 px card radius; 20 px gap between cards. |
| Focus | 2 px `--sc-primary` outline with 3 px offset; never removed. |

---

## 2. Auth screen — login and register

### Existing implemented UI

- Split layout with welcome/auth card and branded panel.
- Login supports password visibility toggle and restores intended destination from route state.
- Register validates password length and match locally.

### Proposed redesigned UI

```text
┌───────────────────────────────┬──────────────────────────────────────┐
│ header: [SC]   Have account?  │ gradient brand panel                 │
│                               │                                      │
│ H1 Welcome back               │ H1 Stay close to your circle         │
│ Body subtitle                 │ 3 benefit rows with icon + copy      │
│ Username/email field          │ decorative layered circles           │
│ Password field + reveal       │                                      │
│ Remember + Forgot*            │                                      │
│ [Sign in]                     │                                      │
│ Create account link           │                                      │
└───────────────────────────────┴──────────────────────────────────────┘
```

| Element | Specification |
| --- | --- |
| Card | 520 px max width, 24 px radius, 32 px padding, layered shadow. |
| Side panel | 44% width at ≥1100 px; hidden at ≤920 px. |
| Heading | H1 32/40 display bold; subtitle body 15/22 muted. |
| Inputs | 48 px height, 12 px radius, 16 px padding, 1 px border. |
| Primary button | 48 px height, full width, 12 px radius, blue gradient, white semibold label. |
| Error | Danger surface `#FEF2F2`, danger text `#B91C1C`, `role="alert"`, 12 px radius. |
| Proposed additions | Email login and `Forgot password?` must be labelled proposed; backend currently authenticates by username and has no reset SPA route. |

---

## 3. Home dashboard / social feed

### Existing implemented UI

- Section heading `YOUR COMMUNITY`, refresh control, stories strip, composer, feed, load-more sentinel.
- Composer supports text, image/video, audience, preview, and publish.
- Feed cards show author, time, audience, media, actions, and comments.

### Proposed redesigned UI

```text
┌────────────────────────────────────────────────────────────────────────┐
│ Eyebrow: HOME          H1 Your community      [Refresh] [New post]     │
│ ───────────────────────────────────────────────────────────────────── │
│ STORIES                                                     See all     │
│ [+ You] [Ava] [Noah] [Mia] [Leo] [Iris] [Omar] [Zoe]                  │
│ ───────────────────────────────────────────────────────────────────── │
│ COMPOSER                                                              │
│ [avatar] What's happening in your circle?                             │
│ [Media] [Audience: Public ▾] [Poll*] [Schedule*]          [Publish]    │
│ ───────────────────────────────────────────────────────────────────── │
│ FEED                                              Newest first ▾      │
│ ┌──────────────────────────────────────────────────────────────────┐ │
│ │ [avatar] Ava Thompson @ava · 18m [Public] [Pinned] [Repost] [•••] │ │
│ │ Design systems update — three patterns we shipped this week.    │ │
│ │ #design #product                                                 │ │
│ │ [16:9 media stage with soft gradient placeholder]               │ │
│ │ ──────────────────────────────────────────────────────────────── │ │
│ │ ♥ 24   💬 8   ↻ 3               [Share] [Save]                  │ │
│ │ [avatar] Write a thoughtful reply...                  [Post]    │ │
│ └──────────────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────────┘
```

| Region | Visual specification |
| --- | --- |
| Page eyebrow | Overline 11/16, 700, uppercase, `--sc-text-muted`, 0.08em tracking. |
| Page title | H1 28/36 display bold. |
| Stories strip | 100 px item width; 64 px avatar ring; 12 px labels; horizontal scroll with snap. |
| Composer | 20 px padding; 16 px avatar; 48 px collapsed textarea; 8 px control gap. |
| Post card | 20 px padding; 18 px radius; 1 px border; 20 px gap to next card. |
| Media stage | 16:9 max; 14 px radius; object-fit cover; tap/click opens media viewer. |
| Action bar | 40 px controls; 8 px gaps; hover surface; pressed state uses blue/teal tint. |
| Comments | Separated by 1 px line; replied comments indented 24 px with left rail. |
| Skeleton | Shimmer 1.4 s, respecting reduced motion; same card geometry as loaded state. |

`Poll` and `Schedule` controls are **proposed surfaces** supported only by backend models/fields; poll CRUD and scheduled publishing are incomplete.

---

## 4. Profile screen

### Existing implemented UI

- Cover image or `No cover photo`, avatar, name, handle, bio, location, website.
- Own profile shows Edit profile; others show follow/friend/message/block actions.
- Stats row and authored posts list.

### Proposed redesigned UI

```text
┌────────────────────────────────────────────────────────────────────────┐
│ cover 240px with 12% dark bottom overlay                              │
│                    [avatar 96px, 4px app-colour ring]                 │
│                    Ava Thompson  ✓  @ava                              │
│                    Product designer · Building calmer communities     │
│                    📍 London   🔗 ava.design   🗓 Joined Mar 2025      │
│                                                                      │
│ OWN: [Edit profile] [Share profile]                                   │
│ OTHER: [Message] [Follow] [Add friend] [••• Block]                    │
│ [ 42 posts ] [ 1.2k followers ] [ 318 following ]                     │
├────────────────────────────────────────────────────────────────────────┤
│ [ Posts ] [ Media ] [ About ]*                                        │
│ [post card] [post card] [post card]                                   │
└────────────────────────────────────────────────────────────────────────┘
```

| Element | Desktop | Mobile |
| --- | --- | --- |
| Cover | 240 px height | 160 px height |
| Avatar | 96 px, overlapping cover by 32 px | 80 px, overlapping by 28 px |
| Identity block | Centered | Centered |
| Actions | 40 px high, 8 px gap | 44 px high, wrapped two rows |
| Stats | 3 equal cells, 16 px dividers | 3 equal cells, 12 px typography |
| Tabs | 44 px, underline active indicator | Full-width segmented control |

`Media` and `About` are **proposed derived views** using existing profile/post data; no new endpoint is required.

---

## 5. Story viewer

### Existing implemented UI

- Full-screen modal, grouped progress bars, author header, pause for non-video, close, previous/next, keyboard navigation, 5-second auto-advance, reduced-motion handling, video end handling, and view recording.

### Proposed redesigned UI

```text
┌──────────────────────────────────────────┐
│ ███████░░░░  ██████░░░░░  ███░░░░░░░  │  progress bars, 3px, top 12px
│ [avatar] Ava · 2h          [Pause] [×]   │  header 56px, white on scrim
│                                          │
│              media stage                 │  9:16 max, centered
│                                          │
│ caption copy                             │  bottom 24px, white, 15px
│ [‹]                               [›]    │  44px circular controls
│ reactions row*                           │  proposed only
└──────────────────────────────────────────┘
```

| Element | Specification |
| --- | --- |
| Backdrop | `#020617` at 92% opacity with 8 px blur. |
| Media stage | Max width 480 px, max height 78vh, 16 px radius. |
| Progress | 3 px bars, 4 px gap, `--sc-surface-inverse` at 45% inactive / 100% active. |
| Header | 56 px; avatar 36 px; typography white; icon controls 36 px with hover surface. |
| Caption | 15/22; max 3 lines before clamp; `aria-live="polite"` for story changes. |
| Reactions | **Proposed** seven-reaction selector; backend endpoint exists but current UI does not expose it. |
| Reduced motion | Disable auto-advance and transitions; user advances manually. |

---

## 6. Messaging screen

### Existing implemented UI

- Two-pane conversation list and chat.
- Search, unread badges, presence, typing, date separators, attachments, WebSocket events, REST fallback send, reconnect backoff.
- Attachment-only messages cannot currently be sent; message edit/delete events are handled but not triggered from UI.

### Proposed redesigned UI

```text
┌────────────────────────┬──────────────────────────────────────────────┐
│ MESSAGES          [+]  │ [avatar] Ava  ● Online      [Search] [•••]   │
│ [ Search conversation ]│                                              │
│ [All][Unread 3][Groups*]│ TODAY                                        │
│ ┌────────────────────┐ │        [received bubble]                     │
│ │[av] Ava ●    10:42 │ │                                              │
│ │ Attachment sent (2)│ │                   [own bubble]  ✓✓ Seen      │
│ └────────────────────┘ │        [image attachment card]               │
│ [av] Noah last msg     │        typing dots…                          │
│ [av] Mia last msg      │                                              │
│                        │ [📎] [ Write a message... ] [Send]           │
└────────────────────────┴──────────────────────────────────────────────┘
```

| Element | Specification |
| --- | --- |
| List pane | 320 px desktop; full width on mobile; 72 px conversation rows. |
| Active row | Blue-tinted surface, 2 px left accent, unread badge 20 px. |
| Chat pane | Max message width 65%; 12 px radius; 16 px bubble padding. |
| Own bubble | Blue gradient surface, white text, right aligned. |
| Received bubble | Neutral raised surface, primary text, left aligned. |
| Date separator | 11 px uppercase label with hairlines. |
| Composer | 56 px footer, 12 px radius input, 44 px controls, safe-area padding on mobile. |
| Attachment | Preview chip with filename/size and remove control; send enabled with attachment only in proposed fix. |
| Typing | 20 px reserved row; three-dot animation disabled under reduced motion. |

`Groups` is a **backend-only / proposed surface**; group REST endpoints exist but there is no group WebSocket or SPA screen.

---

## 7. Notifications screen

### Existing implemented UI

- Type-specific icons/messages, unread styling, live status, refresh, mark-one/mark-all, deep links, WebSocket reconnect.

### Proposed redesigned UI

```text
┌────────────────────────────────────────────────────────────────────────┐
│ NOTIFICATIONS                        ● Live   [Refresh] [Mark all read]│
│ [All] [Unread 3] [Mentions] [Requests]                        [Settings]│
│ ┌────────────────────────────────────────────────────────────────────┐ │
│ │ [icon] Ava liked your post                    2m        [•••]      │ │
│ │ "Design systems update…"  → Open post                            │ │
│ │ [Mark read]                                                       │ │
│ └────────────────────────────────────────────────────────────────────┘ │
│ [icon] Noah started following you             1h                      │
└────────────────────────────────────────────────────────────────────────┘
```

| Element | Specification |
| --- | --- |
| Unread card | Blue-tinted surface, 2 px left accent, bold primary text. |
| Read card | Neutral surface, muted metadata, normal weight. |
| Icon tile | 40 × 40 px, 12 px radius, type colour from token map. |
| Timestamp | 12 px `--sc-text-muted`, aligned right. |
| Preview | 14 px, max two lines, 8 px top gap. |
| CTA | Text link 14 px semibold; deep links to `/posts/:id`, `/users/:id`, `/friend-requests`, `/messages/:id`. |
| Live status | 8 px dot: teal connected, amber reconnecting, slate offline; text 12 px. |

Proposed improvements require backend/SPA changes: pagination, WebSocket updates after read actions, and busy navigation fix.

---

## 8. Admin dashboard

### Existing implemented UI

- Custom Django admin with searchable sidebar, dark theme, toasts, confirmation modal, canvas charts, 12 real-data KPI cards, analytics 7/30/90 ranges, roles, and system pages.

### Proposed redesigned UI

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ [SC] ADMIN       scope selector | search | notifications | theme | avatar   │
├────────────────────┬─────────────────────────────────────────────────────────┤
│ Dashboard          │ H1 Overview        Last 30 days ▾   [Export]*          │
│ Analytics          │ 12 KPI cards in 4 × 3 grid; permission-masked values   │
│ Users / Posts      │ ┌──────────────────────┬──────────────────────┐        │
│ Comments / Likes   │ │ Registrations line   │ Engagement bar       │        │
│ Stories / Reports  │ └──────────────────────┴──────────────────────┘        │
│ Roles / System     │ Recent Users | Recent Posts | Admin Activity          │
└────────────────────┴─────────────────────────────────────────────────────────┘
```

| Element | Specification |
| --- | --- |
| Admin sidebar | 248 px, collapsible groups, permission-aware items. |
| KPI grid | 4 columns ≥1280 px, 3 columns 1024–1279, 2 columns 761–1023, 1–2 columns ≤760. |
| KPI card | 160 px min height, 16 px radius, 20 px padding, label 12 px uppercase, value 28 px bold. |
| Trend chip | Positive teal, negative danger, flat slate; arrow icon plus text. |
| Charts | 320 px height, 16 px padding, gridlines at 10% opacity, legend below. |
| Tables | 44 px rows, sticky header, 12 px cell padding; cards below 760 px. |
| Proposed `Export` | Requires new backend export job; not currently implemented. |

Known source defects to preserve as warnings in design handoff: Likes KPI links to Posts; Pending Reports counts all reports; browser smoke is historical only.

---

## Visual acceptance checklist

- Every screen uses the same 8 px spacing rhythm and 12/16/20 px radius scale.
- Primary actions are always blue, destructive actions danger red, and success/online states teal.
- Every interactive element has a visible focus ring and ≥44 px touch target on mobile.
- Loading states use the same geometry as loaded content.
- Empty states include a short explanation and one relevant next action.
- Proposed-only controls are visually marked in review material and absent from “current UI” screenshots.
- Dark mode uses semantic tokens, not hard-coded colours.
- Reduced motion disables shimmer, auto-advance, and decorative transitions.

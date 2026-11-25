# UI Mockup Specifications

## Design system source

The active visual system is defined mainly in `frontend/src/index.css` (with legacy Vite styles in `frontend/src/App.css`). It is hand-written CSS using custom properties, BEM-like class names, gradient accents, card shadows, and responsive breakpoints. There is no component-library dependency; icons are inline SVG paths from `components/Icon.jsx`.

## Brand and typography

| Token / element | Specification observed in source |
| --- | --- |
| Product name | `SocialConnect`; brand mark is a square `S`. |
| Display font | `Plus Jakarta Sans`, fallback `Inter`, system UI. |
| Body font | `Inter`, fallback `Segoe UI`, system UI. |
| Font weights | 400, 500, 600, 700, 800 loaded from Google Fonts. |
| Base colours | Navy `#172554`, blue `#2563EB`, violet `#8B5CF6`, teal `#0D9488`, amber `#F59E0B`. |
| Primary action | `#2563EB` with `#1D4ED8` hover/dark variant and soft `#EFF6FF`. |
| Accent gradient | `linear-gradient(135deg, #2563EB, #8B5CF6)`. |
| Surfaces | Light background `#F8FAFC`, surface `#FFFFFF`, borders `#E2E8F0`. |
| Text | Primary `#0F172A`, body `#334155`, muted `#64748B`. |
| Radius | Cards `16–22px`, controls `12px`, pills `999px`. |
| Shadows | Layered low-opacity shadows; card shadow combines a tight and wide layer. |
| Focus | `2px solid #2563EB`, `3px` offset; a 3px primary ring token also exists. |

A dark theme is applied by setting `document.documentElement.dataset.theme` from `Navbar`; dedicated `:root[data-theme="dark"]` blocks override surfaces, borders, cards, inputs, and messages.

## Global layout specification

### Authenticated desktop

```text
┌──────────────────────────────────────────────────────────────────────┐
│ Top navbar (sticky): brand | primary icons | search | theme, settings│
│                     profile menu, unread badges                      │
├───────────────┬──────────────────────────────────┬───────────────────┤
│ Left sidebar  │ Main content (<Outlet />)        │ Right rail        │
│ profile card  │ feed / messages / profile / etc. │ suggestions       │
│ primary nav   │ centered max-width column        │ requests/friends  │
│ see more nav  │                                  │ discover cards    │
└───────────────┴──────────────────────────────────┴───────────────────┘
```

- Top navbar height token: `--nav-h: 72px`.
- Left sidebar contains profile summary, primary navigation (`Home`, `Explore`, `Friends`, `Messages`, `Notifications`), and an expandable “See more” group (`Friend requests`, `Saved posts`, `My profile`, `Settings`).
- Right rail is fully populated only on `/`; other routes show a generic “Discover” card plus “Your space” shortcuts.
- Main column uses cards with consistent padding, radius, hover lift, and section headers.

### Mobile

- Top navbar collapses to brand, drawer button, theme toggle, and account controls.
- A fixed bottom navigation bar shows `Home`, `People`, `Friends`, `Chat`, `Alerts`, plus a `More` popover.
- A modal drawer provides all primary and secondary links, with focus trap, backdrop close, Escape close, and body-scroll lock.
- Breakpoints present in the stylesheet include `1320`, `1180`, `1100`, `920`, `760`, `560`, `520`, `500`, `480`, `420`, and `400px`.

## Component specifications

### Buttons

- Primary: blue gradient/solid, pill or rounded radius, elevated hover, white label.
- Secondary: surface border with soft hover.
- Danger: red surface/border, used in destructive confirmations.
- Icon buttons: square/round transparent containers with hover surface and ARIA labels.
- All buttons expose `:focus-visible`, disabled cursor, and busy labels such as `Saving...`, `Sharing...`, `Updating...`.

### Cards

- `.post-card`, `.rail-card`, `.profile-card`, `.search-user-card`, `.auth-card`, and dialog panels share white surface, subtle border, large radius, and layered shadow.
- Hover state for interactive cards uses a slight translate/shadow change under `@media (hover: hover) and (pointer: fine)`.
- Loading skeletons exist for stories, posts, comments, notifications, search results, and notification settings.

### Forms

- Labels use small uppercase or muted typography; error text uses `.form-error` with danger colour and `role="alert"`.
- Inputs have border, radius, hover border emphasis, focus ring, and `aria-invalid` styling.
- `normalizeFieldErrors()` and `getNonFieldError()` in `utils/formErrors.js` map DRF validation errors into field-level and form-level messages.
- File inputs are visually hidden and triggered from styled drop zones or buttons.

### Avatars and media

- `UserAvatar` shows an image when available, otherwise a coloured fallback with the user's initial.
- Interactive avatars open `MediaViewer`; non-interactive avatars render as `role="img"`.
- `MediaViewer` provides close, previous/next, 50–400% zoom, fit, failed-media message, Escape/arrow keys, and focus restoration.
- `getMediaUrl()` resolves relative API media paths against `API_ORIGIN`.

### Stories

- Story strip groups items by author, own story first, then newest activity.
- Unseen rings are visually emphasized; viewed IDs are tracked in component state.
- Viewer is a modal with progress bars, author header, pause (non-video only), close, previous/next, keyboard navigation, 5-second auto-advance, reduced-motion accommodation, and video end handling.
- Creation dialog accepts image/video up to 25 MB, caption up to 500 characters, and privacy `public | followers | friends`; upload progress is displayed.

### Posts and comments

- Composer accepts text and one image in `CreatePost.jsx`; richer audience/poll/draft controls exist in the home page composer but are not fully surfaced everywhere.
- Post action bar shows like count, comment count, share count, bookmark state, and inline comment form.
- Comments are grouped by parent, recursively rendered with cycle protection, and support reply, edit, delete, and confirmation dialogs.
- Optimistic like updates roll back on API failure.

### Messaging and notifications

- Messages page uses a two-pane conversation list/detail layout with search, unread counts, attachment affordance, typing/online indicators, and WebSocket-driven updates.
- Notification page uses unread styling, type-specific iconography, read-all action, filters/tabs, and a WebSocket connection to the notification stream.
- Navbar polls unread message/notification counts every 60 seconds and listens for a custom refresh event.

### Dialogs

- `ConfirmDialog` is an `alertdialog` with focus management, Escape/backdrop cancel, busy state, optional danger styling, and error message slot.
- `NotificationSettingsDialog` uses `role="switch"` toggles for eight preference keys, optimistic updates, rollback on failure, and focus trap.
- Drawer, story viewer, story creator, and media viewer all lock body scroll and restore previous focus.

## Interaction and motion

- Transitions use a standard `0.25s cubic-bezier(0.4, 0, 0.2, 1)` and a spring `0.45s cubic-bezier(0.34, 1.56, 0.64, 1)`.
- `prefers-reduced-motion: reduce` blocks disable animations/transitions; story auto-advance also respects reduced motion.
- Hover effects are gated by `@media (hover: hover) and (pointer: fine)`.
- Skeleton shimmer/pulse is used while data loads.

## Accessibility specifications present in source

- Semantic landmarks: `header`, `nav`, `aside`, `main`, `section`, `form`, `article`.
- ARIA: `aria-label`, `aria-expanded`, `aria-pressed`, `aria-checked`, `aria-current`, `aria-live`, `role="dialog"`, `role="alertdialog"`, `role="switch"`, `role="status"`, `role="alert"`, `role="menu"`.
- Visible `.sr-only` labels for icon-only controls and form inputs.
- Focus trapping in drawer, confirmation, settings, story viewer/creator, and media viewer.
- Keyboard handling for Escape, Tab/Shift+Tab, ArrowLeft/ArrowRight, and story navigation.

## Mockup fidelity notes / inconsistencies

- `index.css` contains multiple repeated theme and responsive blocks (for example around lines 2054/9909, 3964/11804, and 7433/13453). This suggests prior stylesheet restoration/duplication and increases maintenance risk.
- `App.css` is still largely stock Vite starter CSS and is not the active SocialConnect design source.
- `public/icons.svg` is a leftover Vite/social icon sprite and is not referenced by the app.
- `manifest.webmanifest` theme colour and icon set do not match the active SPA theme tokens; only an SVG `favicon.svg` is declared.
- The navbar icon for “Saved posts” uses `Icon name="explore"` in the profile menu, a minor semantic mismatch.
- Theme colour meta is updated dynamically between `#F8FAFC` and `#18191A`, while the static HTML and manifest use `#F8FAFC` and `#2f4858` respectively.

# 01 — Complete Desktop Wireframes

## Scope and conventions

- **Viewport baseline:** 1440 × 900 px; desktop layout remains structurally stable from 1280 px upward.
- **Wireframe type:** structured ASCII layouts with Mermaid state/flow diagrams where helpful.
- **Source of truth:** implemented routes in `frontend/src/App.jsx` and current shell in `AppShell.jsx` / `navbar.jsx`.
- **Separation:** each screen section labels **Existing implemented UI** and **Proposed redesigned UI**.
- **Features shown:** only source-confirmed capabilities. Backend-only ideas are labelled **Proposed surface**.

## Global desktop shell — Existing implemented UI

```text
+------------------------------------------------------------------------------------------------+
| TOP NAVBAR                                                                                      |
| [S] SocialConnect   Home  Explore  Friends  Messages (3)  Alerts (5)   [Search people...]        |
|                                                              [theme] [settings] [@you ▾]        |
+---------------+--------------------------------------------------------------+-----------------+
| LEFT SIDEBAR  | MAIN CONTENT — <Outlet />                                     | RIGHT RAIL      |
| [avatar]      |                                                              | Discover        |
| Your Name     |  route-specific page                                        | suggestions     |
| @username     |                                                              |                 |
| [profile link]|                                                              | Friend requests |
|               |                                                              | Friends         |
| MENU          |                                                              | Shortcuts       |
| > Home        |                                                              |                 |
| > Explore     |                                                              | SocialConnect   |
| > Friends     |                                                              | footer          |
| > Messages    |                                                              |                 |
| > Alerts      |                                                              |                 |
| See more ▾    |                                                              |                 |
+---------------+--------------------------------------------------------------+-----------------+
```

Existing traits:

- Sticky top navbar with unread badges and profile menu.
- Left sidebar with profile summary and expandable “See more”.
- Right rail is fully populated on `/`; other routes use generic discovery/shortcut cards.
- Theme, notification settings dialog, and custom refresh events are wired.

## Global desktop shell — Proposed redesigned UI

```text
+------------------------------------------------------------------------------------------------+
| HEADER 72px                                                                                     |
| [SC logo]  Home   Search   Friends   Messages 3   Alerts 5   [⌘K search]   [☾] [⚙] [avatar ▾]  |
+---------------+--------------------------------------------------------------+-----------------+
| SIDEBAR 264px | CONTENT max-width 780px                                      | RAIL 312px      |
| [profile card]|                                                              | [Suggested]     |
| - avatar      |  section eyebrow / page title / primary action              | - person + Follow|
| - name        |                                                              | [Requests]      |
| - handle      |  card-based content with 20px gaps                          | [Your space]    |
|               |                                                              | [Trending tags]*|
| NAV GROUPS    |                                                              |                 |
| Discover      |                                                              | context-aware   |
| Home, Search  |                                                              | per route       |
| Connect       |                                                              |                 |
| Friends, Req. |                                                              |                 |
| Communicate   |                                                              |                 |
| Messages, Alerts|                                                            |                 |
| Library       |                                                              |                 |
| Bookmarks, Profile, Settings*                                                |                 |
+---------------+--------------------------------------------------------------+-----------------+
```

Proposed refinements:

- Group navigation by intent instead of one long list.
- Make the right rail context-aware (feed suggestions vs conversation tools vs admin links).
- Add a keyboard shortcut affordance (`⌘K` / `Ctrl+K`) for people search.
- Keep existing routes; no invented `/explore` or `/settings` route. “Settings” remains a dialog trigger.
- `Trending tags` is a **proposed backend-only surface** because hashtags exist in the API but no endpoint/page does.

## Auth screens

### Login — Existing implemented UI

```text
+----------------------------------------------------------+
| WELCOME TO SOCIALCONNECT                                 |
| Welcome back                                             |
| Sign in to continue your community.                      |
|                                                          |
| Username   [______________________________]              |
| Password   [______________________________] [Show]       |
| [ note / error ]                                         |
| [ Log in ]                                               |
| New here? Create an account                              |
+----------------------------------------------------------+
```

### Register — Existing implemented UI

```text
+--------------------------------------+  +--------------------------------+
| [SC] Create Account                  |  | Join our growing community!     |
| Username        [________________]   |  | premium welcome copy            |
| Email Address   [________________]   |  | benefit list                    |
| Password        [________________]   |  | branded gradient panel          |
| Confirm Password[________________]   |  |                                |
| [ Create Account ]                   |  |                                |
| Already registered? Log in           |  |                                |
+--------------------------------------+  +--------------------------------+
```

### Proposed auth refinement

```text
+--------------------------------------------------------------------------------+
| [SC]  SocialConnect                                     Already have an account?|
|                                                                                |
|   Welcome back                                     +--------------------------+ |
|   A calmer place to stay close to your people.     |  premium brand panel     | |
|                                                    |  3 benefit cards         | |
|   Username or email*  [______________________]     |  community stats mock    | |
|   Password*           [______________________] [👁] |  gradient mesh           | |
|   [ ] Remember me     Forgot password?*            +--------------------------+ |
|   [ Sign in ]                                                                  |
|   New here? Create an account                                                  |
+--------------------------------------------------------------------------------+
```

`Email` and `Forgot password?` are **proposed** because backend currently authenticates by username only and password-reset screens are backend-only.

## Home / dashboard feed

### Existing implemented UI

```text
+----------------------------------------------------------------------------------+
| YOUR COMMUNITY                                      Home             [Refresh]    |
+----------------------------------------------------------------------------------+
| STORIES                                    [ You ][friend][friend][friend] [‹][›] |
+----------------------------------------------------------------------------------+
| [avatar] Share an update                                                          |
| [ textarea ................................................................. ]  |
| [image v] [Add photo] [Add video] [Remove]  Audience [public v]     [Publish]    |
+----------------------------------------------------------------------------------+
| Latest posts                                              Newest first            |
| [avatar] Name @user · 2h [public]                                  [···]          |
| text ...............................................................            |
| [image gallery]                                                                   |
| [♥ 12] [💬 3] [↻ 1] [Share] [Bookmark]                                            |
| [ Write a comment... ] [Comment]                                                  |
| [Load more posts]                                                                 |
+----------------------------------------------------------------------------------+
```

### Proposed redesigned UI

```text
+----------------------------------------------------------------------------------+
| HOME                                              Newest first   [Refresh] [+]   |
+----------------------------------------------------------------------------------+
| STORIES                                                                      See all|
| + [You]  [Ava]  [Noah]  [Mia]  [Leo]  [Iris]  [Omar]  [Zoe]                       |
+----------------------------------------------------------------------------------+
| COMPOSER                                                                         |
| [avatar] What's happening in your circle?                                       |
| [ media ][ audience: Public ▾ ][ poll* ][ schedule* ]              [ Publish ]    |
+----------------------------------------------------------------------------------+
| FEED                                                                             |
| ┌──────────────────────────────────────────────────────────────────────────────┐ |
| │ [avatar] Ava Thompson  @ava · 18m  [Public]   [pinned] [repost]        [···] │ |
| │ Design systems update — here are three patterns we shipped this week.       │ |
| │ #design #product                                                             │ |
| │ [ media card with soft gradient placeholder ]                               │ |
| │ ─────────────────────────────────────────────────────────────────────────── │ |
| │  ♥ 24 Likes    💬 8 Comments    ↻ 3 Reposts      [Share] [Save]             │ |
| │  [Your avatar] Write a thoughtful reply...                    [Post]        │ |
| └──────────────────────────────────────────────────────────────────────────────┘ |
+----------------------------------------------------------------------------------+
```

`poll*` and `schedule*` are proposed controls for backend-only features.

## Post detail

```text
Existing:                          Proposed:
+------------------------------+   +--------------------------------------------------+
| SHARED POST                  |   | POST                                 [Back]       |
| Shared by @user  [Back home] |   | ┌────────────────────────────────────────────┐   |
| ┌──────────────────────────┐ |   | │ author / audience / time / menu            │   |
| │ post card                 │ |   | │ full media stage                         │   |
| │ media                     │ |   | │ actions rail + comment composer          │   |
| │ PostActions               │ |   | └────────────────────────────────────────────┘   |
| └──────────────────────────┘ |   | Related discussion / thread summary*          |
+------------------------------+   +--------------------------------------------------+
```

## User profile

### Existing implemented UI

```text
+----------------------------------------------------------------------------------+
| [ cover image / No cover photo ]                                                 |
| [avatar] Display Name @username                                                  |
| bio · location · website                                                         |
| OWN: [Edit profile]   OTHER: [Add friend][Follow][Message][Block]                |
| [N posts] [N followers] [N following]                                            |
+----------------------------------------------------------------------------------+
| username's Posts                                                                 |
| [post card] [post card] [post card]                                               |
+----------------------------------------------------------------------------------+
```

### Proposed redesigned UI

```text
+----------------------------------------------------------------------------------+
| [ cover image — 240px, soft overlay ]                                             |
|        [avatar 96px]                                                              |
|        Display Name  ✓  @username                                                 |
|        Bio line 1...                                                              |
|        📍 Location   🔗 website   🗓 Joined                                        |
|                                                                                  |
| OWN PROFILE: [Edit profile] [Share profile]                                       |
| OTHER: [Message] [Follow] [Add friend] [••• Block]                                |
|        [ N posts ][ N followers ][ N following ]                                  |
+----------------------------------------------------------------------------------+
| TABS: [ Posts ] [ Media ] [ About ]*                                              |
| [post card] [post card] [post card]                                               |
+----------------------------------------------------------------------------------+
```

`Media` and `About` are proposed derived views from existing post/profile data; no new backend endpoint is required.

## Edit profile

```text
+----------------------------------------------------------------------------------+
| Edit profile                                                        [Cancel]      |
+----------------------------------------------------------------------------------+
| PROFILE MEDIA                 ACCOUNT DETAILS                                     |
| [avatar preview] [Change]     First name [______]  Last name [______]             |
| [cover preview]  [Change]     Bio [.........................................]    |
| [Remove]                      Location [______]  Website [______]                 |
|                               Privacy: [ ] Private profile                       |
|                               Who can comment [Everyone ▾]                       |
|                               Who can message [Everyone ▾]                       |
|                                                                                  |
|                                                        [ Save changes ]           |
+----------------------------------------------------------------------------------+
```

Proposed redesign adds a two-column form, inline unsaved-changes guard, and explicit retry banner for load failure.

## Search / discover people

```text
Existing:                          Proposed:
+------------------------------+   +--------------------------------------------------+
| GROW YOUR COMMUNITY          |   | DISCOVER PEOPLE                                  |
| Discover people              |   | [ Search by name or @username        ] [Search] |
| [ search input ] [Search]    |   | Suggested for you  [View all]                    |
| [avatar] Name @user          |   | ┌──────┐ ┌──────┐ ┌──────┐                       |
| [Follow] [Add friend]        |   | │person│ │person│ │person│                       |
| [avatar] Name @user          |   | │Follow│ │Follow│ │Follow│                       |
| [Following][Request sent]    |   | └──────┘ └──────┘ └──────┘                       |
+------------------------------+   +--------------------------------------------------+
```

## Connections and friend requests

```text
Connections — Existing                 Friend requests — Existing
+--------------------------------+     +--------------------------------+
| YOUR COMMUNITY                 |     | YOUR CONNECTIONS               |
| [Friends][Followers][Following]|     | [Received (3)] [Sent]          |
| [avatar] Name @user -> profile |     | [avatar] Name @user            |
| [avatar] Name @user -> profile |     | [Accept] [Reject]              |
+--------------------------------+     | [avatar] Name @user            |
                                       | [Cancel request]               |
                                       +--------------------------------+

Proposed refinement: add relationship chips, mutual friends count*, and bulk accept/reject*.
*Mutual friends is backend-only; bulk actions are proposed backend work.
```

## Bookmarks

```text
Existing:                          Proposed:
+------------------------------+   +--------------------------------------------------+
| SAVED FOR LATER  [Refresh]   |   | BOOKMARKS                        [Refresh] [Clear*]|
| [post card]                  |   | Filter: [All] [Public] [Friends] [Followers]      |
| [post card]                  |   | [post card]                                      |
| No bookmarks -> Browse feed  |   | [post card]                                      |
+------------------------------+   +--------------------------------------------------+
```

`Clear all` is proposed only if a bulk-delete endpoint is added; current API supports per-post toggles.

## Messages

### Existing implemented UI

```text
+--------------------------------+------------------------------------------------+
| YOUR INBOX                     | [<] [avatar] Name   [online] Presence           |
| Messages                 [+]   |------------------------------------------------|
| [search conversations...]      | Today                                           |
| [avatar] Name (2)              |            [other bubble]                       |
| last message preview...        |                                                 |
| [avatar] Name                  |                   [own bubble] 10:42 · Seen      |
| [avatar] Name                  | [typing...]                                     |
| No conversations yet -> Search |------------------------------------------------|
|                                | [Attach] [message input...] [Send]              |
+--------------------------------+------------------------------------------------+
```

### Proposed redesigned UI

```text
+--------------------------------+------------------------------------------------+
| MESSAGES                 [+]   | [avatar] Ava  ● Online       [•••] [Search]      |
| [ Search conversations ]       |------------------------------------------------|
| [All] [Unread 3] [Groups*]     | DATE SEPARATOR                                  |
| ┌──────────────────────────┐   |        [received bubble]                         |
| │[av] Ava        ●   10:42 │   |                                                 |
| │ attachment sent     (2) │   |                    [own bubble]  ✓✓ Seen          |
| └──────────────────────────┘   |        [image attachment card]                   |
| [avatar] Noah   last msg       |        typing dots...                           |
| [avatar] Mia   last msg        |------------------------------------------------|
|                                | [paperclip] [ Write a message... ] [Send]       |
+--------------------------------+------------------------------------------------+
```

`Groups` is a proposed surface for backend-only group conversations.

## Notifications

```text
Existing:                          Proposed:
+--------------------------------+  +--------------------------------------------------+
| YOUR UPDATES                   |  | NOTIFICATIONS              ● Live   [Refresh]     |
| 3 unread · Live updates        |  | [All] [Unread 3] [Mentions] [Requests] [Settings] |
| [Refresh] [Mark all read]      |  | ┌────────────────────────────────────────────┐   |
| [*][icon] user liked your post|  | │ [icon] Ava liked your post      2m   [•••] │   |
|    Go to post  [Mark read]    |  | │ Preview text → Open post                   │   |
| [ ][icon] user followed you   |  | └────────────────────────────────────────────┘   |
+--------------------------------+  +--------------------------------------------------+
```

Proposed filters use existing notification types: like, comment, reply, follow, friend_request, message, mention, story_reaction.

## Dialogs and overlays

```text
ConfirmDialog                 Notification settings              Media viewer
+----------------------+       +--------------------------------+  +----------------------+
| !                    |       | Preferences              [x]  |  | [‹] media [›]  [zoom]|
| Delete this post?    |       | Likes                [switch] |  | caption              |
| This cannot be undone|       | Comments             [switch] |  | [1/4]        [Close] |
| [Cancel] [Delete]    |       | Replies / Follows / ...        |  +----------------------+
+----------------------+       | [Done]                         |
                               +--------------------------------+

Story creator                  Story viewer                     Drawer/modal
+----------------------+       +--------------------------------+  +------------------+
| [media preview]      |       | █████░░░ author · 2h  [||][x]  |  | nav list         |
| Caption [........]   |       | [‹]      image/video      [›]  |  | [Close]          |
| Privacy [public v]   |       | caption                        |  +------------------+
| [Share story]        |       +--------------------------------+  
+----------------------+
```

## Admin desktop shell

```text
+------------------------------------------------------------------------------------------------+
| [SC] ADMIN PANEL        [scope: Users/Posts/Comments] [search...] [🔔 4] [☾] [avatar ▾]        |
+---------------------+--------------------------------------------------------------------------+
| DASHBOARD           | WELCOME BACK, ADMIN                                                       |
| Analytics           | Real database metrics                                    [View analytics]  |
| Users               |                                                                          |
| Posts               | +----------+ +----------+ +----------+ +----------+                       |
| Comments            | |Users  1.2k| |Posts 840 | |Reports 7 | |Likes 3.4k|                       |
| Likes               | +----------+ +----------+ +----------+ +----------+                       |
| Stories             | [12 KPI cards total]                                                      |
| Reports             | +--------------------------+ +--------------------------+                 |
| Roles               | | User Growth chart        | | Post Activity chart      |                 |
| Activity            | +--------------------------+ +--------------------------+                 |
| System              | Recent Users | Recent Posts | Recent Admin Activity                      |
+---------------------+--------------------------------------------------------------------------+
```

Detailed admin design is in `16-ADMIN_PANEL_DESIGN.md`.

## Desktop layout acceptance criteria

- Main content column remains centered and never exceeds 780–840 px on feed/profile pages.
- Navigation and right rail stay visible at ≥1280 px; right rail may collapse at 1180 px.
- All dialogs are centered with overlay and restore focus to trigger.
- Sticky header height is 72 px; sidebar width 264 px proposed (existing ~250–280 px acceptable).
- Every interactive element has visible focus and is reachable by keyboard.
- Proposed additions are labelled and do not imply current implementation.

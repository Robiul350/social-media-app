# Wireframes

These wireframes are source-derived ASCII representations, not pixel-perfect screenshots. They show the information architecture and control placement observed in the React pages and shell components.

## Global authenticated desktop shell

```text
+----------------------------------------------------------------------------------------------+
| [S] SocialConnect   Home  Explore  Friends  Messages(3)  Alerts(5)   [search people...]       |
|                                                             [theme] [settings] [@you v]       |
+-------------------+--------------------------------------------------+-----------------------+
| @you              |  <main / Outlet>                                 | DISCOVER              |
| Your Name         |                                                  | Meet your community   |
| [profile link]    |                                                  | [Find people]         |
|                   |                                                  |                       |
| MENU              |                                                  | YOUR SPACE            |
| > Home            |                                                  | Saved posts           |
| > Explore         |                                                  | Notifications         |
| > Friends         |                                                  | My profile            |
| > Messages        |                                                  |                       |
| > Notifications   |                                                  | SocialConnect         |
| See more v        |                                                  |                       |
| +-------------------+--------------------------------------------------+-----------------------+
```

Expanded “See more”:

```text
| Friend requests |
| Saved posts     |
| My profile      |
| Settings        |
```

## Global mobile shell

```text
+--------------------------------+
| [menu] [S] SocialConnect  [@]  |
+--------------------------------+
|                                |
|          <Outlet />            |
|                                |
+--------------------------------+
| Home | People | Friends | Chat | Alerts | More |
+--------------------------------+
```

Drawer:

```text
+--------------------------------+
| [S] SocialConnect        [x]   |
| [@you] Your Name              |
| Home                          |
| Explore                       |
| Friends                       |
| Messages                      |
| Notifications                 |
| Friend requests               |
| Saved posts                   |
| My profile                    |
| Settings                      |
+--------------------------------+
```

## Login / register

```text
Login                                      Register
+------------------------+  +----------------------+---------------------------+
| YOUR COMMUNITY...      |  | [SC] Create Account  | Join our growing community|
| Good conversations...  |  | Username             | ------------------------- |
| - See updates          |  | Email Address        | Promote SocialConnect     |
| - Share moments        |  | Password             |                           |
| - Stay in touch        |  | Confirm Password     |                           |
| A place to connect     |  | [Create Account]     |                           |
+------------------------+  +----------------------+---------------------------+
```

Login card detail:

```text
+--------------------------------------+
| WELCOME TO SOCIALCONNECT             |
| Welcome back                         |
| Sign in to continue your community.  |
| Username [________________]          |
| Password [________________] [Show]   |
| [ Log in ]                           |
| New here? Create an account          |
+--------------------------------------+
```

## Home feed

```text
+----------------------------------------------------------------------------------+
| YOUR COMMUNITY                                      Home          [Refresh]       |
+----------------------------------------------------------------------------------+
| STORIES                                Moments from your circle        [<] [>]   |
| [+] [you] [friend] [friend] [friend] ...                                          |
+----------------------------------------------------------------------------------+
| [avatar] Share an update                                                          |
| [ textarea ............................................................... ]    |
| [image v] [Add photo] [Add video] [Remove file]  Audience [public v]  [Publish] |
+----------------------------------------------------------------------------------+
| Latest posts                                              Newest first           |
| [avatar] Name  @user · 2h  [public]                                  [...]        |
| Post text ...............................................................       |
| [image gallery buttons]                                                           |
| [♡ Like] 12 Likes  [3 Comments]  1 Share  [Share]  [Bookmark]                     |
| [ Write a comment... ] [Comment]                                                  |
+----------------------------------------------------------------------------------+
| [Loading more...] / [Load more posts]                                             |
+----------------------------------------------------------------------------------+
```

Story viewer modal:

```text
+---------------------------------------------+
| ██████░░░░  [avatar] username · time  [||][x]|
| [<]        image / video / text       [>]   |
| caption text (when media + text)            |
+---------------------------------------------+
```

Post menu:

```text
Owner:                    Non-owner:
+----------------+        +----------------+
| Edit post      |        | Repost         |
| Pin to profile |        | Report reasons |
| Delete post    |        | [Submit report]|
+----------------+        +----------------+
```

## User profile

```text
+-----------------------------------------------------------------------------------+
| [cover image / No cover photo]                                                    |
| [avatar] Display Name   @username                                                  |
| Bio text ...                                                                      |
| Location row / Website row                                                        |
|                                                                                   |
| OWN PROFILE:                          OTHER PROFILE:                              |
| [Edit profile]                        [Add friend] [Follow] [Message] [Block]     |
|                                       or Request sent / Accept / Friends states  |
|                                                                                   |
| [N posts] [N followers] [N following]                                             |
+-----------------------------------------------------------------------------------+
| username's Posts                                                                  |
| [post card with media + PostActions]                                              |
+-----------------------------------------------------------------------------------+
```

## Search

```text
+--------------------------------------------------------+
| GROW YOUR COMMUNITY                                    |
| Discover people                                        |
| Search by name or username              [Search]       |
+--------------------------------------------------------+
| [avatar] Display Name @username                        |
| bio ...                                                |
| [Follow] [Add friend]                                  |
| [avatar] Display Name @username                        |
| [Following] [Request sent · Cancel]                    |
+--------------------------------------------------------+
```

## Connections

```text
+-----------------------------------------------------------+
| YOUR COMMUNITY                                            |
| Friends / Followers / Following      [Friend requests]    |
| [Friends] [Followers] [Following]                         |
+-----------------------------------------------------------+
| [avatar] Display Name @username  -> /users/:id            |
| [avatar] Display Name @username  -> /users/:id            |
+-----------------------------------------------------------+
```

## Friend requests

```text
+-------------------------------------------------------------+
| YOUR CONNECTIONS                                            |
| Friend requests                [View connections] [Discover]|
| [ Received (3) ] [ Sent ]                                   |
+-------------------------------------------------------------+
| [avatar] Name @user                                         |
| [Accept] [Reject]                                           |
| [avatar] Name @user                                         |
| [Cancel request]                                            |
+-------------------------------------------------------------+
```

## Messages

```text
Desktop:
+-----------------------+------------------------------------------------+
| YOUR INBOX            | [<] [avatar] Name   [online dot] Presence      |
| Messages         [+]  |------------------------------------------------|
| [search conversations]| Today                                          |
| [avatar] Name   (2)   |                 [other bubble]                  |
| last message...       |                                                 |
| [avatar] Name         |        [own bubble] 10:42 · Seen                |
| [avatar] Name         |        typing...                                |
| No conversations...   |------------------------------------------------|
|                       | [Attach] [message input...] [Send]              |
+-----------------------+------------------------------------------------+

Mobile (conversation selected):
+--------------------------------+
| [<] [avatar] Name  [online]    |
+--------------------------------+
| date separator                 |
| [other bubble]                 |
|        [own bubble] · Seen     |
| typing...                      |
+--------------------------------+
| [Attach] [message...] [Send]   |
+--------------------------------+
```

## Notifications

```text
+--------------------------------------------------------------+
| YOUR UPDATES                                                 |
| Notifications        3 unread · Live updates connected       |
| [Refresh] [Mark all read]                                    |
+--------------------------------------------------------------+
| [*] [icon] user liked your post          2m                  |
|     Go to post                              [Mark read]      |
| [ ] [icon] user started following you      1h                 |
|     Go to profile                                            |
+--------------------------------------------------------------+
```

## Bookmarks

```text
+---------------------------------------------------------------+
| SAVED FOR LATER                                               |
| Bookmarks                                        [Refresh]    |
+---------------------------------------------------------------+
| [post card] author, content, media, PostActions               |
| [post card] author, content, media, PostActions               |
| No bookmarks yet -> Browse your feed                          |
+---------------------------------------------------------------+
```

## Edit profile

```text
+--------------------------------------------------+
| Edit profile                                     |
| Loading your profile... / error block            |
| First name [________] Last name [________]        |
| Bio [......................................]     |
| Location [________] Website [________]            |
| [x] Private profile                              |
| Who can comment [everyone v]                     |
| Who can message [everyone v]                     |
| Profile picture [Choose] [preview] [Remove]      |
| Cover photo     [Choose] [preview] [Remove]      |
| [ Save changes ]                                 |
+--------------------------------------------------+
```

## Dialogs

```text
ConfirmDialog                 Notification settings
+----------------------+       +--------------------------------+
| !                    |       | PREFERENCES                    |
| Delete this post?    |       | Notification settings      [x]|
| This cannot be undone|       | Likes                 [switch]|
| [Cancel] [Delete]    |       | Comments              [switch]|
+----------------------+       | Replies / Follows / ...        |
                               | [Done]                         |
                               +--------------------------------+
```

## Modal relationships

```mermaid
flowchart LR
    Home --> StoryViewer[Story viewer]
    Home --> PostEdit[Post edit dialog]
    Home --> Confirm[Confirm delete]
    Home --> Media[Media viewer]
    Profile --> Confirm
    Profile --> Media
    Bookmarks --> Media
    PostDetail --> Media
    PostActions --> Confirm
    Navbar --> Settings[Notification settings]
    AppShell --> Settings
    Navbar --> LogoutConfirm[Logout confirmation]
```

## Wireframe caveats

- Wireframes describe implemented routes/components only; `/explore` and `/settings` are not SPA pages.
- Backend-only features (poll voting UI, group chat UI, hashtag pages, moderation UI, report status workflow, message edit/delete controls) are intentionally absent.
- Modal dimensions, spacing, and exact breakpoints are defined in `UI_MOCKUP_SPECIFICATIONS.md` and `frontend/src/index.css`.

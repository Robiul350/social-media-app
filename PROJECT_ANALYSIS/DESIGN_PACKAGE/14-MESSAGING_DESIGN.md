# 14 — Messaging Design

## Purpose

This document specifies direct messaging, conversation list, chat pane, real-time events, attachments, read receipts, presence, typing, edit/delete proposal, and group-chat proposal.

## Existing implemented UI

`Messages.jsx` is the most complex real-time screen:

- Two-pane conversation list and chat on desktop; one pane on mobile.
- Conversation search.
- Unread badges and online indicators.
- Chat history with date separators.
- REST send with fallback and WebSocket send.
- Attachment support with MIME/size checks.
- Typing indicator and presence events.
- Read receipts.
- WebSocket reconnect with exponential backoff.
- Handling for `message_updated` and `message_deleted` events.

### Current limitations

- Attachment-only messages cannot be sent: send button and handler require non-empty text.
- Message edit/delete events are handled but no UI triggers them.
- No chat history pagination.
- Strict `===` comparisons can mismatch numeric/string IDs.
- Shared `error` state mixes loading, send, read, and socket failures.
- Reconnect probe result is fetched but ignored.
- Group chat REST endpoints exist but no group UI or group WebSocket.

---

## Desktop layout

```text
┌────────────────────────┬──────────────────────────────────────────────┐
│ MESSAGES          [+]  │ [avatar] Ava  ● Online      [Search] [•••]   │
│ [ Search conversations ]│                                              │
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

| Region | Desktop | Mobile |
| --- | --- | --- |
| List pane | 320 px | Full screen. |
| Chat pane | Remaining width | Full screen, replaces list. |
| Conversation row | 72 px | 72 px. |
| Header | 64 px | 60 px. |
| Composer | 64 px | 56 px + safe area. |
| Message bubble max | 65% of chat width | 78% of chat width. |

---

## Conversation list

### Anatomy

- Avatar with presence dot.
- Display name.
- Last message preview or `Attachment`.
- Timestamp.
- Unread badge.
- Active selection indicator.
- Search field.

### States

| State | Treatment |
| --- | --- |
| Active | Blue-tinted surface, 2 px left accent. |
| Unread | Bold preview, count badge, accessible `N unread` label. |
| Read | Neutral surface. |
| Online | Teal dot plus `Online` text in header. |
| Offline | Slate dot. |
| Search match | Highlighted text; no layout shift. |
| No results | `No conversations found.` clear search. |
| Empty | `No conversations yet.` CTA `Find people`. |
| Loading | Row skeletons. |
| Error | Retry card. |
| Groups* | Proposed filter; backend-only group list exists. |

### Search rules

- Local search over loaded conversations.
- Debounce if server-side search is added later.
- Preserve selection when filtering.
- Announce result count politely.

---

## Chat pane

### Anatomy

- Header: back (mobile), avatar, name, presence, search*, more*.
- Date separators.
- Received and own bubbles.
- Attachment cards.
- Typing row.
- Composer with attach, textarea, send.

### Bubble specification

| Element | Own bubble | Received bubble |
| --- | --- | --- |
| Surface | Blue gradient. | Neutral raised surface. |
| Text | White 14/20. | Primary text 14/20. |
| Radius | 14 px with 4 px tail corner. | 14 px with 4 px tail corner. |
| Padding | 12 px 14 px. | 12 px 14 px. |
| Timestamp | Right, white 70% opacity. | Right, muted. |
| Read receipt | `✓✓ Seen` under bubble. | Not shown. |
| Attachment | Preview card inside bubble. | Preview card inside bubble. |
| Max width | 65% desktop / 78% mobile. | Same. |

### Message states

| State | Visual / behaviour |
| --- | --- |
| Sending | 60% opacity, pending indicator. |
| Sent | Normal bubble. |
| Delivered | Normal bubble; no read tick. |
| Read | Own bubble shows read receipt. |
| Failed | Danger outline and retry action. |
| Edited | `Edited` caption. |
| Deleted | Removed from list; soft delete on backend. |
| Attachment loading | Skeleton thumbnail + filename. |
| Attachment failed | Neutral placeholder + retry/remove. |

---

## Composer and attachments

### Existing issue

Both the send button and `sendMessage()` handler require non-empty text, so an attachment-only message cannot be sent.

### Proposed rule

Enable send when either:

- text has non-whitespace content, **or**
- a valid attachment is selected.

```text
[📎] [ Write a message... or attach a file ] [Send]
      attachment chip: report.pdf · 1.2 MB  [×]
```

### Attachment specification

- Max 25 MB.
- Allowed MIME prefixes from backend serializer.
- Preview chip with filename, size, remove control.
- Upload progress if implemented; otherwise busy state.
- Attachment-only send uses REST FormData path with empty `content` allowed by backend.
- Error preserves attachment and text.

### Composer states

| State | Behaviour |
| --- | --- |
| Empty | Send disabled. |
| Text only | Send enabled. |
| Attachment only | Send enabled in proposed fix. |
| Uploading | Busy label; duplicate send blocked. |
| Socket offline | REST fallback allowed; show neutral status. |
| Send error | Inline error with retry; preserve input. |
| Success | Clear text and attachment; scroll to latest. |

---

## Real-time event design

| Event | Direction | UI effect |
| --- | --- | --- |
| `chat_message` | WS inbound | Append bubble; update last message/unread if not active. |
| `typing` / `typing_update` | Client/server | Show/hide typing row. |
| `presence_update` / `presence` | Server | Update online dot/text. |
| `read_receipt` | Server | Mark own message IDs as read. |
| `message_updated` | REST-originated WS | Replace bubble text and show `Edited`. |
| `message_deleted` | REST-originated WS | Remove bubble with optional fade. |
| `error` | Server | Show inline send error. |

### Proposed event contract fix

REST POST broadcast currently omits `sender_username`, while the WebSocket consumer includes it. The UI should normalise a single `chat_message` shape:

```json
{
  "type": "chat_message",
  "id": 123,
  "message_id": 123,
  "sender": 7,
  "sender_username": "ava",
  "content": "Hello",
  "attachment": null,
  "created_at": "2026-11-25T10:42:00Z"
}
```

Normalise IDs with `Number()` or consistent strings to avoid strict comparison failures.

---

## Presence and typing

### Presence

- Derived from WebSocket presence events and list state.
- Header shows dot + text: `Online`, `Offline`, `Connecting…`, `Reconnecting…`.
- Do not emit false offline presence for rejected sockets; fix in `chat/consumers.py`.

### Typing

- Client emits typing frames on input with debounce.
- Server broadcasts typing to peer.
- Typing row reserves 20 px to avoid layout jump.
- Auto-clear after inactivity or server timeout.
- Animation disabled under reduced motion.

---

## Read receipts and unread counts

- REST read action marks peer messages read and broadcasts message IDs.
- Own messages show `✓✓ Seen`.
- Conversation unread badge clears when active conversation is read.
- Navbar polls `chat/unread-count/` every 60 s and listens to custom events.
- Proposed: push unread count changes over WebSocket instead of polling-only.

---

## Edit and delete UI proposal

Backend supports PATCH/DELETE and broadcasts update/delete for direct messages; UI currently lacks controls.

### Proposed controls

```text
Own bubble hover/tap → [•••] → [Edit] [Delete]
Edit mode → inline textarea → [Save] [Cancel]
Delete → ConfirmDialog → soft delete
```

Rules:

- Only message owner sees controls.
- Delete uses `ConfirmDialog`.
- Edited caption appears under bubble.
- Socket events from other clients update the same message.
- Group message edit/delete currently lacks WS broadcast; do not promise real-time group updates.

---

## Group chat proposal

### Backend facts

- `GroupConversation`, `GroupMembership`, group create/list, group message list/create exist.
- Creator receives admin role; others member.
- `role`, `muted`, `archived` fields are unused by API/UI.
- No group WebSocket route or membership management endpoints found.

### Proposed surface — not implemented

```text
MESSAGES [All][Unread][Groups]
[Create group] → name, avatar, member picker (max 50 others)
Group conversation header → [Members] [Mute*] [Archive*] [Add member*]
```

Items marked `*` require new backend endpoints/WS support.

### Status statement

Group chat is **Backend only / Partial**. Do not include it in current UI screenshots or claim real-time group messaging until a group consumer and SPA screen exist.

---

## Connection states

| State | Treatment |
| --- | --- |
| Connecting | Header `Connecting…`; composer disabled or REST fallback available. |
| Connected | Presence/typing live. |
| Reconnecting | Non-blocking amber status; exponential backoff. |
| Offline | Neutral banner; REST send fallback where allowed. |
| Auth expired | Proposed reconnect with refreshed ticket; current WS closes. |
| Blocked / no permission | Chat unavailable; neutral explanation. |
| Conversation missing | Empty state, not error dump. |

Reconnect proposal: merge the probe result already fetched by current code into state instead of discarding it.

---

## Accessibility requirements

- Conversation list is a labelled navigation list.
- Chat transcript has `role="log"` and `aria-live="polite"` for new messages.
- Composer label is explicit; Send has accessible name.
- Attachment remove button names the file.
- Read receipts are text, not icon-only.
- Typing status announced politely.
- Edit/delete menus follow menu button keyboard patterns.
- Mobile back control returns to conversation list and restores focus.
- Reduced motion disables typing dots and message fade.

---

## Acceptance criteria

- Two-pane desktop and single-pane mobile layouts implemented.
- Conversation search, unread badges, presence, typing, and read receipts work.
- Attachment-only messages can be sent in proposed implementation.
- Edit/delete controls trigger existing endpoints and render WS events.
- Message IDs are normalised consistently.
- Reconnect recovers missed messages.
- Group chat remains labelled backend-only/proposed.
- All connection and message states have visible treatment.

# Data Dictionary

Source: current Django model and migration files. Primary keys are implicit BigAutoField IDs unless stated. Privacy is enforced in application query layers, not database row-level security.

## Tables

| ID | Table | Attributes | Notes |
| --- | --- | --- | --- |
| DB-TBL-001 | `users_user` | id (BigAutoField), username (unique), email (unique), password, first_name, last_name, is_staff, is_active, is_superuser, date_joined, last_login, email_verified | AbstractUser; username login; email_verified has no writer |
| DB-TBL-002 | `users_profile` | id, user (1-1), profile_picture, cover_photo, bio, location, website, date_of_birth, is_private, allow_comments, allow_messages, is_verified, social_links, education, work, created_at, updated_at | Auto-created by signal |
| DB-TBL-003 | `users_story` | id, author FK, media, text, privacy, expires_at, created_at | M2M viewers through StoryView; 24-hour expiry |
| DB-TBL-004 | `users_storyview` | id, story FK, viewer FK, viewed_at | Unique (story, viewer) |
| DB-TBL-005 | `users_storyreaction` | id, user FK, story FK, reaction_type, created_at, updated_at | Unique (user, story); seven reaction types |
| DB-TBL-006 | `users_adminaction` | id, created_at, action_type, target_type, target_id, target_label, description, metadata | Inert: no actor, no writer, not admin-registered |
| DB-TBL-007 | `posts_post` | id, author FK, content, image, video, audience, is_draft, is_pinned, scheduled_for, repost_of self-FK, created_at, updated_at | Visibility in social/access.py |
| DB-TBL-008 | `posts_postimage` | id, post FK, image, position | Ordered gallery; no API writer |
| DB-TBL-009 | `posts_bookmark` | id, post FK, user FK, created_at | Unique (post, user) |
| DB-TBL-010 | `posts_poll` | id, post OneToOne, question, expires_at | No poll CRUD endpoint |
| DB-TBL-011 | `posts_polloption` | id, poll FK, text | Vote target |
| DB-TBL-012 | `posts_pollvote` | id, option FK, user FK | Unique (option, user), not (poll, user) |
| DB-TBL-013 | `posts_hashtag` | id, name unique | M2M with Post; regex sync from post text |
| DB-TBL-014 | `posts_postreport` | id, post FK, reporter FK, reason, created_at | No status or resolution field |
| DB-TBL-015 | `social_like` | id, post FK, user FK, created_at | Unique (post, user) |
| DB-TBL-016 | `social_comment` | id, post FK, user FK, content, parent self-FK, created_at, updated_at | Threaded replies |
| DB-TBL-017 | `social_mention` | id, comment FK nullable, post FK nullable, mentioned FK, created_at | No exclusive-or DB constraint |
| DB-TBL-018 | `social_commentreaction` | id, comment FK, user FK, reaction, created_at | Unique (comment, user); no UI |
| DB-TBL-019 | `social_follow` | id, follower FK, following FK, created_at | Unique directional pair |
| DB-TBL-020 | `social_block` | id, blocker FK, blocked FK, created_at | Unique pair; DB self-block check; index on blocker/created_at |
| DB-TBL-021 | `social_friendrequest` | id, sender FK, receiver FK, status, created_at, updated_at | Unique direction; status pending/accepted/rejected; self-request check |
| DB-TBL-022 | `notifications_notification` | id, recipient FK, sender FK, notification_type, post FK nullable, comment FK nullable, is_read, created_at | IDs masked when target is not visible |
| DB-TBL-023 | `notifications_notificationpreference` | id, user OneToOne, likes, comments, replies, follows, friend_requests, messages, mentions, story_reactions | Eight opt-out booleans |
| DB-TBL-024 | `chat_groupconversation` | id, name, avatar, created_by FK, created_at | M2M members through GroupMembership |
| DB-TBL-025 | `chat_groupmembership` | id, group FK, user FK, role, muted, archived | Unique (group, user); role/mute/archive unused in source |
| DB-TBL-026 | `chat_message` | id, sender FK, receiver FK nullable, group FK nullable, content, attachment, edited_at, deleted_at, is_read, created_at | Soft delete; no exclusive-or DB constraint |

## Relationship summary

| Parent | Child | Cardinality | Key / through |
| --- | --- | --- | --- |
| `User` | `Profile` | 1—1 | user |
| `User` | `Post` | 1—N | author |
| `User` | `Story` | 1—N | author |
| `Story` | `User` | M—N | viewers through StoryView |
| `Story` | `StoryReaction` | 1—N | reactions |
| `Post` | `PostImage` | 1—N | images |
| `Post` | `Poll` | 1—1 | poll |
| `Poll` | `PollOption` | 1—N | options |
| `PollOption` | `PollVote` | 1—N | votes |
| `Post` | `Hashtag` | M—N | hashtags |
| `Post` | `Comment` | 1—N | comments |
| `Comment` | `Comment` | 1—N | parent replies |
| `Post` | `Like` | 1—N | likes |
| `User` | `Follow` | 1—N | follower/following |
| `User` | `Block` | 1—N | blocker/blocked |
| `User` | `FriendRequest` | 1—N | sender/receiver |
| `Notification` | `User` | N—1 | recipient/sender |
| `User` | `NotificationPreference` | 1—1 | notification_preferences |
| `GroupConversation` | `User` | M—N | members through GroupMembership |
| `Message` | `User` | N—1 | sender/receiver |
| `Message` | `GroupConversation` | N—1 | group |

## Constraints and application-level invariants

- Unique pairs: profile↔user, story view, story reaction, bookmark, like, comment reaction, follow direction, block direction, friend-request direction, group membership.
- DB check constraints: `block_not_self`, `friend_request_not_self`.
- View-level invariants: one vote per poll per user, post visibility/audience, self-action guards, message target construction, soft-delete filtering, story expiry/privacy.
- Known gaps: `PostReport` has no status; `PollVote` uniqueness is per option only; `Message` has no exclusive receiver/group constraint; `PostImage` has no writer; `Mention` has no exclusive target constraint.
- `django.contrib.admin.models.LogEntry` is the actual admin activity source. `AdminAction` is dormant.

- Migration alignment: `manage.py makemigrations --check --dry-run` returned `No changes detected`; applied runtime state is [NOT VERIFIED - USER CONFIRMATION REQUIRED].

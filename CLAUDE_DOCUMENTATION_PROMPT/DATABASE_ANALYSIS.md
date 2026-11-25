# Database Analysis

Source of truth: current Django model files plus migration files under each app. Historical database documents were only used as a cross-check.

## 1. Persistence overview

| Fact | Evidence |
| --- | --- |
| Database engine is PostgreSQL; no SQLite fallback is present. | `backend/config/settings.py`; `AGENTS.md`. |
| `AUTH_USER_MODEL = "users.User"`. | `backend/config/settings.py`. |
| Primary keys are implicit Django `BigAutoField` IDs unless overridden. | Model source and initial migrations. |
| Privacy is enforced in application query layers (`social/access.py`), not database row-level security. | `backend/social/access.py`, view code. |
| Chat deletion is soft (`Message.deleted_at`); verified read paths exclude non-null `deleted_at`. | `chat/models.py`, `chat/views.py`, `chat/consumers.py`. |
| Migration chains exist for all five apps: `users` 0001–0007, `posts` 0001–0002, `social` 0001–0005, `notifications` 0001–0006, `chat` 0001–0002. | Files under `backend/*/migrations/`. |

---

## 2. Users app

### DB-TBL-001 — `users_user`

Extends `AbstractUser`.

| Field | Type / options | Notes |
| --- | --- | --- |
| Inherited | `password`, `last_login`, `is_superuser`, `username` (unique, max 150), `first_name`, `last_name`, `is_staff`, `is_active`, `date_joined`, `groups`, `user_permissions` | Standard Django auth fields. Login uses username, not email. |
| `email` | `EmailField(unique=True)` | Required unique email. |
| `email_verified` | `BooleanField(default=False)` | No writer or verification endpoint found in source. |

### DB-TBL-002 — `users_profile`

One-to-one with `User` via `user`, `related_name="profile"`.

| Field | Type / options |
| --- | --- |
| `profile_picture` | `ImageField(upload_to="profile/")`, blank/null |
| `cover_photo` | `ImageField(upload_to="cover/")`, blank/null |
| `bio` | `TextField`, blank/null |
| `location` | `CharField(max_length=150)`, blank/null |
| `website` | `URLField`, blank/null |
| `date_of_birth` | `DateField`, blank/null |
| `is_private` | `BooleanField(default=False)` |
| `allow_comments` | `CharField(max_length=10)`, choices `everyone/followers/friends/nobody`, default `everyone` |
| `allow_messages` | Same choices/default as `allow_comments` |
| `is_verified` | `BooleanField(default=False)`; read-only in serializer |
| `social_links` | `JSONField(default=dict)`, blank |
| `education`, `work` | `CharField(max_length=250)`, blank, default `""` |
| `created_at`, `updated_at` | auto timestamp fields |

Auto-created by `users.signals.create_user_profile` on user creation; signal is imported by `users/apps.py:ready()`.

### DB-TBL-003 — `users_story`

| Field | Type / options |
| --- | --- |
| `author` | FK → `User`, `CASCADE`, `related_name="stories"` |
| `media` | `FileField(upload_to="stories/")`, blank/null |
| `text` | `CharField(max_length=500)`, blank, default `""` |
| `privacy` | `CharField(max_length=10)`, choices `public/followers/friends`, default `public` |
| `expires_at` | `DateTimeField`; server-set to creation time + 24 hours |
| `viewers` | M2M → `User` through `StoryView`, `related_name="viewed_stories"` |
| `created_at` | `auto_now_add` |

Ordering: `["-created_at"]`.

### DB-TBL-004 — `users_storyview`

Through model for story views.

- `story` FK → `Story`, `CASCADE`, `related_name="story_views"`.
- `viewer` FK → `User`, `CASCADE`, `related_name="story_views"`.
- `viewed_at` auto timestamp.
- Unique constraint `unique_story_view` on `(story, viewer)`.

### DB-TBL-005 — `users_storyreaction`

- `user` FK → `User`, `related_name="story_reactions"`.
- `story` FK → `Story`, `related_name="reactions"`.
- `reaction_type` choices: `like`, `love`, `care`, `haha`, `wow`, `sad`, `angry`.
- `created_at`, `updated_at`.
- Unique constraint `unique_user_story_reaction` on `(user, story)`.
- Ordering: `["-created_at"]`.

### DB-TBL-006 — `users_adminaction`

Defined in `users/admin_action.py` and imported into `users/models.py` to preserve migration state.

- Fields: `created_at`, `action_type` (16 choices), `target_type`, `target_id`, `target_label`, `description`, `metadata` JSON.
- No actor field and no writer found in source.
- Not registered in admin and not used as the dashboard activity source; `django.contrib.admin.models.LogEntry` is used instead.

---

## 3. Posts app

### DB-TBL-007 — `posts_post`

| Field | Type / options | Notes |
| --- | --- | --- |
| `author` | FK → `User`, `CASCADE`, `related_name="posts"` | Author-only writes in views. |
| `content` | `TextField`, blank/null | No DB constraint requiring content or media. |
| `image` | `ImageField(upload_to="posts/images/")`, blank/null | ≤10 MB validated in serializer/view. |
| `video` | `FileField(upload_to="posts/videos/")`, blank/null | ≤100 MB validated in serializer/view. |
| `audience` | `CharField(max_length=10)`, `public/followers/friends`, default `public` | Enforced by `social/access.py`. |
| `is_draft` | `BooleanField(default=False)` | Hiding behavior in views. |
| `is_pinned` | `BooleanField(default=False)` | No ordering consumer found. |
| `scheduled_for` | `DateTimeField`, blank/null | Future posts hidden in read paths; no publisher job found. |
| `repost_of` | FK → self, `SET_NULL`, blank/null, `related_name="reposts"` | Repost source. |
| `created_at`, `updated_at` | auto timestamps | — |

Ordering: `["-created_at"]`.

### Other posts tables

| ID | Model | Fields / constraints | Notes |
| --- | --- | --- | --- |
| DB-TBL-008 | `PostImage` | `post` FK CASCADE (`images`), `image` ImageField, `position` PositiveInteger default 0 | Ordering by `position`; no API writer found. |
| DB-TBL-009 | `Bookmark` | `post` FK, `user` FK, `created_at`; unique `(post,user)` named `unique_post_bookmark` | Toggle endpoint. |
| DB-TBL-010 | `Poll` | OneToOne → `Post` (`poll`), `question` CharField(250), `expires_at` blank/null | No poll CRUD endpoint found. |
| DB-TBL-011 | `PollOption` | `poll` FK (`options`), `text` CharField(120) | Vote target. |
| DB-TBL-012 | `PollVote` | `option` FK (`votes`), `user` FK (`poll_votes`); unique `(option,user)` | DB uniqueness is per option, not per poll; view-level single-vote check exists. |
| DB-TBL-013 | `Hashtag` | `name` unique; M2M → `Post` (`hashtags`) | Populated by regex sync on post create/update. |
| DB-TBL-014 | `PostReport` | `post` FK, `reporter` FK, `reason` CharField(250), `created_at` | No status/resolution field; create-only endpoint. |

---

## 4. Social app

### DB-TBL-015 — `Like`

- `post` FK (`likes`), `user` FK (`post_likes`), `created_at`.
- Unique constraint `unique_post_like` on `(post, user)`.

### DB-TBL-016 — `Comment`

- `post` FK (`comments`), `user` FK (`user_comments`), `content` TextField.
- `parent` FK → self, `CASCADE`, blank/null, `related_name="replies"`.
- `created_at`, `updated_at`; ordering by `created_at`.

### DB-TBL-017 — `Mention`

- `comment` FK blank/null (`mentions`), `post` FK blank/null (`mentions`).
- `mentioned` FK → `User` (`mentions`), `created_at`.
- No DB constraint requiring exactly one target object.
- Not registered in admin.

### DB-TBL-018 — `CommentReaction`

- `comment` FK (`reactions`), `user` FK (`comment_reactions`).
- `reaction` CharField(max_length=10) with six choices, default `like`.
- Unique constraint `unique_comment_reaction` on `(comment, user)`.
- Not registered in admin.

### DB-TBL-019 — `Follow`

- `follower` FK (`following`), `following` FK (`followers`), `created_at`.
- Unique constraint `unique_user_follow` on `(follower, following)`; direction matters.

### DB-TBL-020 — `Block`

- `blocker` FK (`blocks_created`), `blocked` FK (`blocks_received`), `created_at`.
- Unique constraint `unique_user_block` on `(blocker, blocked)`.
- Check constraint `block_not_self` = `~Q(blocker=F("blocked"))`.
- Index on `(blocker, created_at)`. Migration hard-codes the name `social_bloc_blocker_c353a5_idx` while the model declares an unnamed index. `manage.py makemigrations --check --dry-run` was executed during this audit and returned `No changes detected`, so there is no current model/migration drift. Runtime application state remains `[NOT VERIFIED - USER CONFIRMATION REQUIRED]`.

### DB-TBL-021 — `FriendRequest`

- `sender` FK (`sent_friend_requests`), `receiver` FK (`received_friend_requests`).
- `status` CharField(max_length=10): `pending/accepted/rejected`, default `pending`.
- `created_at`, `updated_at`.
- Unique constraint `unique_friend_request_direction` on `(sender, receiver)`.
- Check constraint `friend_request_not_self` = `~Q(sender=F("receiver"))`.
- Indexes: `(receiver, status, -created_at)` named `friendreq_rcv_stat_ct`; `(sender, status, -created_at)` named `friendreq_snd_stat_ct`.

---

## 5. Notifications app

### DB-TBL-022 — `Notification`

- `recipient` FK (`notifications`), `sender` FK (`sent_notifications`).
- `notification_type`: `like`, `comment`, `reply`, `follow`, `friend_request`, `message`, `mention`, `story_reaction`.
- `post` FK blank/null (`notifications`), `comment` FK blank/null (`notifications`).
- `is_read` BooleanField(default=False), `created_at`.
- Ordering: `["-created_at"]`.
- Serializer masks `post`/`comment` IDs when the requester no longer has visibility.

### DB-TBL-023 — `NotificationPreference`

- OneToOne → `User`, `related_name="notification_preferences"`.
- Eight booleans default `True`: `likes`, `comments`, `replies`, `follows`, `friend_requests`, `messages`, `mentions`, `story_reactions`.

---

## 6. Chat app

### DB-TBL-024 — `GroupConversation`

- `name` CharField(max_length=120).
- `members` M2M → `User` through `GroupMembership`, `related_name="group_conversations"`.
- `avatar` ImageField(upload_to="chat/groups/"), blank/null.
- `created_by` FK → `User`, `related_name="created_groups"`.
- `created_at`.

### DB-TBL-025 — `GroupMembership`

- `group` FK (`memberships`), `user` FK (`group_memberships`).
- `role` CharField(max_length=10): `member/admin`, default `member`.
- `muted`, `archived` booleans; no API consumer found.
- Unique constraint `unique_group_membership` on `(group, user)`.

### DB-TBL-026 — `Message`

- `sender` FK (`sent_messages`), `receiver` FK blank/null (`received_messages`), `group` FK blank/null (`messages`).
- `content` TextField.
- `attachment` FileField(upload_to="chat/attachments/"), blank/null.
- `edited_at`, `deleted_at` DateTimeFields blank/null.
- `is_read` BooleanField.
- `created_at`.
- Ordering: `["created_at"]`.
- No DB constraint enforcing exactly one of `receiver`/`group`; application code filters the target type.
- All read paths must exclude non-null `deleted_at`.

---

## 7. Migration history

| App | Migrations | Notable schema changes |
| --- | --- | --- |
| `users` | `0001_initial`, `0002_remove_user_bio_remove_user_cover_photo_and_more`, `0003_profile_allow_comments_profile_allow_messages_and_more`, `0004_profile_education_profile_is_verified_and_more`, `0005_user_email_verified`, `0006_adminaction`, `0007_storyreaction` | Moved user profile fields into `Profile`; added privacy/comment/message settings; added Story/StoryView; added `email_verified`; added `AdminAction`; added `StoryReaction`. |
| `posts` | `0001_initial`, `0002_post_audience_post_is_draft_post_is_pinned_and_more` | Created Post and related models; added audience, draft, pin, scheduled, repost, hashtags, polls, images, reports, bookmarks, votes and constraints. |
| `social` | `0001_initial`, `0002_follow`, `0003_friendrequest`, `0004_block`, `0005_mention_commentreaction` | Created Like/Comment; added Follow; added FriendRequest with checks/indexes; added Block with check/index; added Mention and CommentReaction. |
| `notifications` | `0001_initial`, `0002`–`0004` choice expansions, `0005_notificationpreference`, `0006_alter_notification_notification_type` | Created Notification; expanded notification types including mention/story_reaction; added preferences. |
| `chat` | `0001_initial`, `0002_message_attachment_message_deleted_at_and_more` | Created Message; added attachment/edited/deleted fields and nullable receiver; added GroupConversation/GroupMembership. |

---

## 8. Relationship summary for ER diagrams

- `User` 1—1 `Profile`.
- `User` 1—N `Post`, `Story`, `Like`, `Comment`, `Follow` (both directions), `Block` (both directions), `FriendRequest` (sender/receiver), `Bookmark`, `PollVote`, `StoryView`, `StoryReaction`, `CommentReaction`, `Mention`, `Notification` (recipient/sender), `Message` (sender/receiver), `GroupMembership`, `GroupConversation.created_by`.
- `Story` 1—N `StoryView` and `StoryReaction`; M2M to `User` through `StoryView`.
- `Post` 1—N `PostImage`, `Like`, `Comment`, `Bookmark`, `PostReport`; 1—1 `Poll`; self-referential reposts; M2M `Hashtag`.
- `Poll` 1—N `PollOption`; `PollOption` 1—N `PollVote`.
- `Comment` self-referential replies; 1—N `Mention`, `CommentReaction`.
- `GroupConversation` M2M `User` through `GroupMembership`; 1—N `Message` when `group` is set.
- `Notification` optionally references `Post` and `Comment`.

---

## 9. Application-level invariants not enforced by the database

| Invariant | Enforcement location | Gap |
| --- | --- | --- |
| Post has content or media | Serializer/view validation | No DB check constraint. |
| One active vote per poll per user | Vote view uses `select_for_update` | DB uniqueness is per `(option,user)`, not `(poll,user)`. |
| No self-block | DB check constraint `block_not_self` | Enforced by DB. |
| No self-friend-request | DB check constraint `friend_request_not_self` plus view guard | Enforced by DB. |
| No self-follow / self-like / self-react / self-message | View/consumer guards | No DB check constraints for these cases. |
| Visibility/audience/block filtering | `social/access.py` and views | Application layer only; raw ORM bypass is possible. |
| Direct or group message target | View/consumer construction | No DB exclusive-or constraint. |
| Mention has exactly one target object | Comment creation view | No DB constraint. |
| Only author can edit/delete own post/comment/message | View permissions | Application layer only. |
| Chat reads exclude soft-deleted messages | Every message queryset | Application convention; easy to miss in new code. |
| Story visibility and 24-hour expiry | Story list/detail access helpers | Application layer only. |

## 10. Test evidence for schema-level behavior

- `manage.py makemigrations --check --dry-run` was executed during the source audit and returned `No changes detected`; the model definitions and migration files are aligned.
- The suite contains 65 test methods across five files. Current pass/fail output is `[NOT VERIFIED - USER CONFIRMATION REQUIRED]` unless the suite is run.
- API tests strongly verify post authorship, draft visibility, hashtag sync, repost idempotence, one vote per user per poll at view level, story privacy/expiry/reactions, block propagation, friend-request state, chat soft delete, JWT/WebSocket close codes, and admin permission masking.
- Database constraints are mostly exercised indirectly through API duplicate/rejection tests; no direct concurrent-transaction or raw-ORM constraint tests were found.
- Weak or absent coverage includes `NotificationPreference` opt-out suppression, mention creation, comment reactions, poll expiry, `PostImage`, `PostReport` moderation, `StoryView` idempotence, chat `edited_at`, valid attachment acceptance, and group membership fields.

## 11. Proposed database improvements

Keep this section clearly separate from implemented behavior.

1. Add a DB constraint preventing more than one `PollVote` per user per poll, not merely per option.
2. Add a `status`/`resolved_at`/`resolver` lifecycle to `PostReport` if moderation is in scope.
3. Add a DB check that a `Message` targets exactly one of `receiver` or `group`.
4. Add a writer API for `PostImage` or remove the model if single-image posts are the intended product.
5. Add a persisted login-event table if analytics must report true logins instead of refresh-token proxies.
6. Add an actor field and writer path to `AdminAction`, or remove it in favour of `LogEntry`.
7. Consider explicit indexes on high-traffic filtered columns if performance testing indicates a need.
8. Define a media authorization strategy; direct file URLs are not privacy-aware.

`[NOT VERIFIED - USER CONFIRMATION REQUIRED]` applies to whether each proposed change is desired by the project owner.

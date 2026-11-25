# Database Design

## Persistence model

The backend uses PostgreSQL through the Django ORM. `AUTH_USER_MODEL = "users.User"`. All primary keys are implicit `BigAutoField` IDs. Unless noted, models have no explicit `Meta.indexes`, and uniqueness is declared with `UniqueConstraint`. Migration chains are present for all five apps; the final source model state is described below.

## Users app

### `User` (extends `AbstractUser`)

| Field | Type / options | Notes |
| --- | --- | --- |
| Inherited | `password`, `last_login`, `is_superuser`, `username` (unique, max 150), `first_name`, `last_name`, `is_staff`, `is_active`, `date_joined`, `groups`, `user_permissions` | Standard Django auth fields. Login uses username, not email. |
| `email` | `EmailField(unique=True)` | Required unique email. |
| `email_verified` | `BooleanField(default=False)` | No endpoint or writer found. |

### `Profile` (OneToOne → `User`, `related_name="profile"`)

| Field | Type / options |
| --- | --- |
| `profile_picture`, `cover_photo` | `ImageField(upload_to="profile/" | "cover/")`, blank/null |
| `bio` | `TextField`, blank/null |
| `location` | `CharField(150)`, blank/null |
| `website` | `URLField`, blank/null |
| `date_of_birth` | `DateField`, blank/null |
| `is_private` | `BooleanField(False)` |
| `allow_comments`, `allow_messages` | `CharField(10)`, choices `everyone/followers/friends/nobody`, default `everyone` |
| `is_verified` | `BooleanField(False)`; read-only in serializer |
| `social_links` | `JSONField(default=dict)`, blank |
| `education`, `work` | `CharField(250)`, blank default `""` |
| `created_at`, `updated_at` | auto timestamps |

Auto-created by `users.signals.create_user_profile` on user creation.

### `Story`

| Field | Type / options |
| --- | --- |
| `author` | FK → `User`, CASCADE, `related_name="stories"` |
| `media` | `FileField(upload_to="stories/")`, blank/null |
| `text` | `CharField(500)`, blank default `""` |
| `privacy` | `CharField(10)`, choices `public/followers/friends`, default `public` |
| `expires_at` | `DateTimeField` (server-set to now + 24 h) |
| `viewers` | M2M → `User` through `StoryView`, `related_name="viewed_stories"` |
| `created_at` | auto_now_add |

`Meta.ordering = ["-created_at"]`.

### `StoryView`

- `story` FK → `Story` CASCADE (`story_views`), `viewer` FK → `User` CASCADE (`story_views`), `viewed_at` auto.
- `UniqueConstraint(story, viewer)` named `unique_story_view`.

### `StoryReaction`

- `user` FK → `User` (`story_reactions`), `story` FK → `Story` (`reactions`).
- `reaction_type`: `like/love/care/haha/wow/sad/angry`.
- `created_at`, `updated_at`.
- `UniqueConstraint(user, story)` named `unique_user_story_reaction`; ordering `-created_at`.

### `AdminAction`

Imported from `users/admin_action.py`. Fields: `created_at`, `action_type` (16 choices), `target_type`, `target_id`, `target_label`, `description`, `metadata` JSON. **No actor field and no code writes to it**; admin audit uses Django `LogEntry`.

## Posts app

### `Post`

| Field | Type / options |
| --- | --- |
| `author` | FK → `User` CASCADE (`posts`) |
| `content` | `TextField`, blank/null |
| `image` | `ImageField(upload_to="posts/images/")`, blank/null |
| `video` | `FileField(upload_to="posts/videos/")`, blank/null |
| `audience` | `CharField(10)`, `public/followers/friends`, default `public` |
| `is_draft`, `is_pinned` | Boolean flags, default False |
| `scheduled_for` | `DateTimeField`, blank/null |
| `repost_of` | FK → self, SET_NULL, blank/null (`reposts`) |
| `created_at`, `updated_at` | auto timestamps |

`Meta.ordering = ["-created_at"]`. No DB constraint requires content or media; that is serializer-level only.

### Other posts models

| Model | Fields / constraints |
| --- | --- |
| `PostImage` | `post` FK CASCADE (`images`), `image` ImageField, `position` PositiveInteger default 0; ordering `position`. No API writer. |
| `Bookmark` | `post` FK, `user` FK, `created_at`; unique `(post,user)` (`unique_post_bookmark`). |
| `Poll` | OneToOne → `Post` (`poll`), `question` CharField(250), `expires_at` blank/null. |
| `PollOption` | `poll` FK (`options`), `text` CharField(120). |
| `PollVote` | `option` FK (`votes`), `user` FK (`poll_votes`); unique `(option,user)` — not unique per poll. |
| `Hashtag` | `name` unique; M2M → `Post` (`hashtags`). Populated by regex sync from post content. |
| `PostReport` | `post` FK, `reporter` FK, `reason` CharField(250), `created_at`. No status/resolution field. |

## Social app

### `Like`

- `post` FK (`likes`), `user` FK (`post_likes`), `created_at`.
- Unique `(post,user)` named `unique_post_like`.

### `Comment`

- `post` FK (`comments`), `user` FK (`user_comments`), `content` TextField.
- `parent` FK → self, CASCADE, blank/null (`replies`).
- `created_at`, `updated_at`; ordering `created_at`.

### `Mention`

- `comment` FK blank/null (`mentions`), `post` FK blank/null (`mentions`), `mentioned` FK → `User` (`mentions`), `created_at`.
- No constraint requiring exactly one target object; not registered in admin.

### `CommentReaction`

- `comment` FK (`reactions`), `user` FK (`comment_reactions`), `reaction` CharField(10) with six choices, default `like`.
- Unique `(comment,user)` named `unique_comment_reaction`; not registered in admin.

### `Follow`

- `follower` FK (`following`), `following` FK (`followers`), `created_at`.
- Unique `(follower,following)` named `unique_user_follow` (direction matters).

### `Block`

- `blocker` FK (`blocks_created`), `blocked` FK (`blocks_received`), `created_at`.
- Unique `(blocker,blocked)` named `unique_user_block`.
- Check constraint `block_not_self`: `~Q(blocker=F("blocked"))`.
- Index on `(blocker, created_at)`; migration hard-codes name `social_bloc_blocker_c353a5_idx`, while model declares unnamed index — confirm with `makemigrations --check --dry-run`.

### `FriendRequest`

- `sender` FK (`sent_friend_requests`), `receiver` FK (`received_friend_requests`).
- `status` CharField(10): `pending/accepted/rejected`, default `pending`.
- `created_at`, `updated_at`.
- Unique `(sender,receiver)` named `unique_friend_request_direction`.
- Check `friend_request_not_self`: `~Q(sender=F("receiver"))`.
- Indexes: `(receiver,status,-created_at)` named `friendreq_rcv_stat_ct`; `(sender,status,-created_at)` named `friendreq_snd_stat_ct`.

## Notifications app

### `Notification`

- `recipient` FK (`notifications`), `sender` FK (`sent_notifications`).
- `notification_type`: `like/comment/reply/follow/friend_request/message/mention/story_reaction`.
- `post` FK blank/null (`notifications`), `comment` FK blank/null (`notifications`).
- `is_read` Boolean default False, `created_at` auto.
- Ordering `-created_at`. Serializer masks `post`/`comment` IDs when the requester can no longer see them.

### `NotificationPreference`

- OneToOne → `User` (`notification_preferences`).
- Eight booleans default True: `likes`, `comments`, `replies`, `follows`, `friend_requests`, `messages`, `mentions`, `story_reactions`.

## Chat app

### `GroupConversation`

- `name` CharField(120), `members` M2M → `User` through `GroupMembership` (`group_conversations`).
- `avatar` ImageField(upload_to="chat/groups/") blank/null.
- `created_by` FK → `User` (`created_groups`), `created_at`.

### `GroupMembership`

- `group` FK (`memberships`), `user` FK (`group_memberships`).
- `role` CharField(10): `member/admin`, default `member`.
- `muted`, `archived` booleans (no API consumer found).
- Unique `(group,user)` named `unique_group_membership`.

### `Message`

- `sender` FK (`sent_messages`), `receiver` FK blank/null (`received_messages`), `group` FK blank/null (`messages`).
- `content` TextField, `attachment` FileField(upload_to="chat/attachments/") blank/null.
- `edited_at`, `deleted_at` DateTimeFields blank/null; `is_read` Boolean; `created_at`.
- Ordering `created_at`.
- No DB constraint enforcing exactly one of `receiver`/`group`; all read paths must filter `deleted_at__isnull=True`.

## Migration history

| App | Migrations | Notable changes |
| --- | --- | --- |
| users | `0001`–`0007` | User fields moved into `Profile`; privacy/comment/message settings; Story/StoryView; `email_verified`; `AdminAction`; `StoryReaction`. |
| posts | `0001`–`0002` | Post; audience/draft/pin/scheduled/repost; Hashtag, Poll, PollOption, PostImage, PostReport, Bookmark, PollVote and constraints. |
| social | `0001`–`0005` | Like/Comment; Follow; FriendRequest with indexes/checks; Block with index/check; Mention/CommentReaction. |
| notifications | `0001`–`0006` | Notification; type-choice expansions (including mention/story_reaction); `NotificationPreference`. |
| chat | `0001`–`0002` | Message; attachment/edited/deleted fields; nullable receiver; GroupConversation/GroupMembership. |

## Design observations

- Centralized access helpers (`social/access.py`) implement privacy policy in query layer rather than database Row-Level Security; misuse of raw ORM queries could bypass it.
- Soft deletion is used for messages; other content is hard-deleted via CASCADE.
- Several intended invariants are application-enforced only: content-or-media on posts, one vote per poll, no self-block/friend request (the latter two do have checks), single notification target for mentions, direct-or-group message target.
- `PostReport` and `AdminAction` are incomplete audit/moderation artifacts.
- No explicit `db_index` was declared on high-traffic foreign keys beyond the named Block/FriendRequest indexes; Django creates FK indexes automatically.
- Upload paths are predictable (`profile/`, `cover/`, `stories/`, `posts/images/`, `posts/videos/`, `chat/attachments/`, `chat/groups/`); production media auth should be reviewed.

## Verification note

`manage.py makemigrations --check --dry-run` was **not executed** as part of this read-only audit. The potential Block index-name drift noted above should be checked before claiming zero migration drift.

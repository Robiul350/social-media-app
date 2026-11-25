# ER Diagram

The diagrams below reflect the current Django model source. All primary keys are implicit `BigAutoField` IDs. Optional FKs are shown with `o{`/`|o` style relationships. For full field options, see `DATABASE_DESIGN.md`.

## Core identity, content, stories, and notifications

```mermaid
erDiagram
    USER ||--o| PROFILE : "has"
    USER ||--o{ POST : "authors"
    USER ||--o{ STORY : "authors"
    STORY ||--o{ STORY_VIEW : "records"
    USER ||--o{ STORY_VIEW : "views"
    STORY ||--o{ STORY_REACTION : "receives"
    USER ||--o{ STORY_REACTION : "makes"
    USER ||--o{ ADMIN_ACTION : "targets metadata only"
    POST ||--o| POST_IMAGE : "may have"
    POST ||--o{ BOOKMARK : "is saved by"
    USER ||--o{ BOOKMARK : "saves"
    POST ||--o| POLL : "may have"
    POLL ||--o{ POLL_OPTION : "has"
    POLL_OPTION ||--o{ POLL_VOTE : "receives"
    USER ||--o{ POLL_VOTE : "casts"
    POST }o--o{ HASHTAG : "tagged with"
    POST ||--o{ POST_REPORT : "is reported in"
    USER ||--o{ POST_REPORT : "reports"
    USER ||--o{ NOTIFICATION : "receives"
    USER ||--o{ NOTIFICATION : "sends"
    POST |o--o{ NOTIFICATION : "optional context"
    COMMENT |o--o{ NOTIFICATION : "optional context"
    USER ||--o| NOTIFICATION_PREFERENCE : "configures"

    USER {
        bigint id PK
        string username UK
        string email UK
        boolean email_verified
        boolean is_active
        datetime date_joined
    }
    PROFILE {
        bigint id PK
        bigint user_id FK "unique"
        string profile_picture
        string cover_photo
        text bio
        string location
        string website
        date date_of_birth
        boolean is_private
        string allow_comments
        string allow_messages
        boolean is_verified
        json social_links
        string education
        string work
    }
    STORY {
        bigint id PK
        bigint author_id FK
        string media
        string text
        string privacy
        datetime expires_at
        datetime created_at
    }
    STORY_VIEW {
        bigint id PK
        bigint story_id FK
        bigint viewer_id FK
        datetime viewed_at
    }
    STORY_REACTION {
        bigint id PK
        bigint story_id FK
        bigint user_id FK
        string reaction_type
    }
    POST {
        bigint id PK
        bigint author_id FK
        text content
        string image
        string video
        string audience
        boolean is_draft
        boolean is_pinned
        datetime scheduled_for
        bigint repost_of_id FK
        datetime created_at
    }
    POST_IMAGE {
        bigint id PK
        bigint post_id FK
        string image
        int position
    }
    BOOKMARK {
        bigint id PK
        bigint post_id FK
        bigint user_id FK
        datetime created_at
    }
    POLL {
        bigint id PK
        bigint post_id FK "unique"
        string question
        datetime expires_at
    }
    POLL_OPTION {
        bigint id PK
        bigint poll_id FK
        string text
    }
    POLL_VOTE {
        bigint id PK
        bigint option_id FK
        bigint user_id FK
    }
    HASHTAG {
        bigint id PK
        string name UK
    }
    POST_REPORT {
        bigint id PK
        bigint post_id FK
        bigint reporter_id FK
        string reason
        datetime created_at
    }
    NOTIFICATION {
        bigint id PK
        bigint recipient_id FK
        bigint sender_id FK
        string notification_type
        bigint post_id FK
        bigint comment_id FK
        boolean is_read
        datetime created_at
    }
    NOTIFICATION_PREFERENCE {
        bigint id PK
        bigint user_id FK "unique"
        boolean likes
        boolean comments
        boolean replies
        boolean follows
        boolean friend_requests
        boolean messages
        boolean mentions
        boolean story_reactions
    }
    ADMIN_ACTION {
        bigint id PK
        string action_type
        string target_type
        bigint target_id
        string target_label
        text description
        json metadata
        datetime created_at
    }
```

## Social graph

```mermaid
erDiagram
    USER ||--o{ LIKE : "gives"
    POST ||--o{ LIKE : "receives"
    USER ||--o{ COMMENT : "writes"
    POST ||--o{ COMMENT : "has"
    COMMENT ||--o{ COMMENT : "parent of replies"
    COMMENT ||--o{ MENTION : "may mention"
    POST ||--o{ MENTION : "may mention"
    USER ||--o{ MENTION : "is mentioned"
    COMMENT ||--o{ COMMENT_REACTION : "receives"
    USER ||--o{ COMMENT_REACTION : "makes"
    USER ||--o{ FOLLOW : "follower side"
    USER ||--o{ FOLLOW : "following side"
    USER ||--o{ FRIEND_REQUEST : "sender side"
    USER ||--o{ FRIEND_REQUEST : "receiver side"
    USER ||--o{ BLOCK : "blocker side"
    USER ||--o{ BLOCK : "blocked side"

    LIKE {
        bigint id PK
        bigint post_id FK
        bigint user_id FK
        datetime created_at
    }
    COMMENT {
        bigint id PK
        bigint post_id FK
        bigint user_id FK
        bigint parent_id FK
        text content
        datetime created_at
    }
    MENTION {
        bigint id PK
        bigint comment_id FK
        bigint post_id FK
        bigint mentioned_id FK
        datetime created_at
    }
    COMMENT_REACTION {
        bigint id PK
        bigint comment_id FK
        bigint user_id FK
        string reaction
    }
    FOLLOW {
        bigint id PK
        bigint follower_id FK
        bigint following_id FK
        datetime created_at
    }
    FRIEND_REQUEST {
        bigint id PK
        bigint sender_id FK
        bigint receiver_id FK
        string status
        datetime created_at
    }
    BLOCK {
        bigint id PK
        bigint blocker_id FK
        bigint blocked_id FK
        datetime created_at
    }
```

## Chat

```mermaid
erDiagram
    USER ||--o{ GROUP_CONVERSATION : "creates"
    USER ||--o{ GROUP_MEMBERSHIP : "has"
    GROUP_CONVERSATION ||--o{ GROUP_MEMBERSHIP : "contains"
    USER ||--o{ MESSAGE : "sends"
    USER |o--o{ MESSAGE : "receives directly"
    GROUP_CONVERSATION |o--o{ MESSAGE : "hosts"

    GROUP_CONVERSATION {
        bigint id PK
        string name
        string avatar
        bigint created_by_id FK
        datetime created_at
    }
    GROUP_MEMBERSHIP {
        bigint id PK
        bigint group_id FK
        bigint user_id FK
        string role
        boolean muted
        boolean archived
    }
    MESSAGE {
        bigint id PK
        bigint sender_id FK
        bigint receiver_id FK
        bigint group_id FK
        text content
        string attachment
        datetime edited_at
        datetime deleted_at
        boolean is_read
        datetime created_at
    }
```

## Relationship notes

- `PROFILE.user` and `NOTIFICATION_PREFERENCE.user` are OneToOne; each user has at most one of each.
- `STORY_VIEW(story, viewer)`, `STORY_REACTION(user, story)`, `BOOKMARK(post, user)`, `LIKE(post, user)`, `FOLLOW(follower, following)`, `COMMENT_REACTION(comment, user)`, and `GROUP_MEMBERSHIP(group, user)` are explicitly unique.
- `BLOCK` and `FRIEND_REQUEST` also have check constraints preventing self-referential rows.
- `FRIEND_REQUEST(sender, receiver)` is unique per direction; a reverse request is a separate row and is handled by the view.
- `POLL_VOTE` is unique per `(option, user)`, **not** per `(poll, user)`; one-vote-per-poll is enforced in the view, not the database.
- `MESSAGE` may target either `receiver` or `group`; the schema does not enforce exactly one. Every read path must exclude soft-deleted rows.
- `MENTION` may reference a comment or a post; the schema does not enforce exactly one.
- `POST.repost_of` is a self-FK with `SET_NULL`, preserving reposts when the source is deleted.
- M2M relations: `STORY.viewers` through `StoryView`, `HASHTAG.posts`, `GROUP_CONVERSATION.members` through `GroupMembership`.

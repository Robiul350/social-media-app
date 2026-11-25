
from django.db import models
from django.conf import settings
from posts.models import Post


class Like(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="likes"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="post_likes"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["post", "user"],
                name="unique_post_like"
            )
        ]

    def __str__(self):
        return f"{self.user.username} liked post {self.post.id}"


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="user_comments"
    )
    content = models.TextField()
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        related_name="replies",
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.user.username}: {self.content[:30]}"


class Mention(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name="mentions", null=True, blank=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="mentions", null=True, blank=True)
    mentioned = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="mentions")
    created_at = models.DateTimeField(auto_now_add=True)


class CommentReaction(models.Model):
    class Reaction(models.TextChoices):
        LIKE = "like", "Like"
        LOVE = "love", "Love"
        HAHA = "haha", "Haha"
        WOW = "wow", "Wow"
        SAD = "sad", "Sad"
        ANGRY = "angry", "Angry"

    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name="reactions")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comment_reactions")
    reaction = models.CharField(max_length=10, choices=Reaction.choices, default=Reaction.LIKE)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["comment", "user"], name="unique_comment_reaction")]



class Follow(models.Model):
    follower = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="following"
    )
    following = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="followers"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["follower", "following"],
                name="unique_user_follow"
            )
        ]

    def __str__(self):
        return (
            f"{self.follower.username} follows "
            f"{self.following.username}"
        )


class Block(models.Model):
    blocker = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="blocks_created",
    )
    blocked = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="blocks_received",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["blocker", "blocked"],
                name="unique_user_block",
            ),
            models.CheckConstraint(
                condition=~models.Q(blocker=models.F("blocked")),
                name="block_not_self",
            ),
        ]
        indexes = [
            models.Index(fields=["blocker", "created_at"]),
        ]

    def __str__(self):
        return f"{self.blocker.username} blocked {self.blocked.username}"


class FriendRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        ACCEPTED = "accepted", "Accepted"
        REJECTED = "rejected", "Rejected"

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_friend_requests",
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="received_friend_requests",
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["sender", "receiver"],
                name="unique_friend_request_direction",
            ),
            models.CheckConstraint(
                condition=~models.Q(sender=models.F("receiver")),
                name="friend_request_not_self",
            ),
        ]
        indexes = [
            models.Index(
                fields=["receiver", "status", "-created_at"],
                name="friendreq_rcv_stat_ct",
            ),
            models.Index(
                fields=["sender", "status", "-created_at"],
                name="friendreq_snd_stat_ct",
            ),
        ]

    def __str__(self):
        return f"{self.sender.username} → {self.receiver.username} ({self.status})"

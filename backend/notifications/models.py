
from django.db import models
from django.conf import settings


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ("like", "Like"),
        ("comment", "Comment"),
        ("reply", "Reply"),
        ("follow", "Follow"),
        ("friend_request", "Friend request"),
        ("message", "Message"),
        ("mention", "Mention"),
        ("story_reaction", "Story reaction"),
    ]

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications"
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_notifications"
    )
    notification_type = models.CharField(
        max_length=20,
        choices=NOTIFICATION_TYPES
    )
    post = models.ForeignKey(
        "posts.Post",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notifications"
    )
    comment = models.ForeignKey(
        "social.Comment",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notifications"
    )
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return (
            f"{self.sender.username} - "
            f"{self.notification_type} - "
            f"{self.recipient.username}"
        )


class NotificationPreference(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notification_preferences")
    likes = models.BooleanField(default=True)
    comments = models.BooleanField(default=True)
    replies = models.BooleanField(default=True)
    follows = models.BooleanField(default=True)
    friend_requests = models.BooleanField(default=True)
    messages = models.BooleanField(default=True)
    mentions = models.BooleanField(default=True)
    story_reactions = models.BooleanField(default=True)

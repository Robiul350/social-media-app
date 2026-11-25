
from django.db import models
from django.conf import settings


class GroupConversation(models.Model):
    name = models.CharField(max_length=120)
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, through="GroupMembership", related_name="group_conversations")
    avatar = models.ImageField(upload_to="chat/groups/", blank=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="created_groups")
    created_at = models.DateTimeField(auto_now_add=True)


class GroupMembership(models.Model):
    group = models.ForeignKey(GroupConversation, on_delete=models.CASCADE, related_name="memberships")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="group_memberships")
    role = models.CharField(max_length=10, choices=[("member", "Member"), ("admin", "Admin")], default="member")
    muted = models.BooleanField(default=False)
    archived = models.BooleanField(default=False)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["group", "user"], name="unique_group_membership")]


class Message(models.Model):
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_messages"
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="received_messages",
        null=True,
        blank=True,
    )
    group = models.ForeignKey(GroupConversation, on_delete=models.CASCADE, related_name="messages", null=True, blank=True)
    content = models.TextField()
    attachment = models.FileField(upload_to="chat/attachments/", blank=True, null=True)
    edited_at = models.DateTimeField(blank=True, null=True)
    deleted_at = models.DateTimeField(blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        target = self.receiver.username if self.receiver else self.group.name
        return f"{self.sender.username} to {target}"

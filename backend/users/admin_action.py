from django.db import models
from django.conf import settings


class AdminAction(models.Model):
    """Audit log for administrative actions performed in the admin dashboard."""

    class ActionType(models.TextChoices):
        USER_CREATE = "user_create", "User Created"
        USER_UPDATE = "user_update", "User Updated"
        USER_DEACTIVATE = "user_deactivate", "User Deactivated"
        USER_ACTIVATE = "user_activate", "User Activated"
        USER_DELETE = "user_delete", "User Deleted"
        POST_CREATE = "post_create", "Post Created"
        POST_UPDATE = "post_update", "Post Updated"
        POST_DELETE = "post_delete", "Post Deleted"
        POST_PIN = "post_pin", "Post Pinned/Unpinned"
        COMMENT_DELETE = "comment_delete", "Comment Deleted"
        REPORT_REVIEW = "report_review", "Report Reviewed"
        REPORT_RESOLVE = "report_resolve", "Report Resolved"
        REPORT_REJECT = "report_reject", "Report Rejected"
        ROLE_CHANGE = "role_change", "Role Changed"
        SETTINGS_UPDATE = "settings_update", "Settings Updated"
        OTHER = "other", "Other Action"

    created_at = models.DateTimeField(auto_now_add=True)
    action_type = models.CharField(max_length=30, choices=ActionType.choices)
    target_type = models.CharField(max_length=50, blank=True)
    target_id = models.BigIntegerField(blank=True, null=True)
    target_label = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.action_type} — {self.target_label or 'N/A'}"
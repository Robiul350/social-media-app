from django.contrib import admin

from .models import Notification, NotificationPreference


@admin.action(description="Mark selected notifications as read")
def mark_as_read(modeladmin, request, queryset):
    updated = queryset.update(is_read=True)
    modeladmin.message_user(request, f"Marked {updated} notification(s) as read.")


@admin.action(description="Mark selected notifications as unread")
def mark_as_unread(modeladmin, request, queryset):
    updated = queryset.update(is_read=False)
    modeladmin.message_user(request, f"Marked {updated} notification(s) as unread.")


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "recipient",
        "sender",
        "notification_type",
        "is_read",
        "created_at",
    )
    list_filter = ("notification_type", "is_read", "created_at")
    search_fields = (
        "recipient__username",
        "sender__username",
    )
    actions = (mark_as_read, mark_as_unread)
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    list_select_related = ("recipient", "sender", "post", "comment")


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "likes",
        "comments",
        "replies",
        "follows",
        "friend_requests",
        "messages",
        "mentions",
        "story_reactions",
    )
    list_filter = (
        "likes",
        "comments",
        "replies",
        "follows",
        "friend_requests",
        "messages",
        "mentions",
        "story_reactions",
    )
    search_fields = ("user__username", "user__email")
    ordering = ("user__username",)
    list_select_related = ("user",)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

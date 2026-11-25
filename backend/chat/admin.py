from django.contrib import admin

from .models import GroupConversation, GroupMembership, Message


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "sender",
        "receiver",
        "group",
        "is_read",
        "deleted_at",
        "created_at",
    )
    list_filter = ("is_read", "group", "created_at")
    search_fields = (
        "sender__username",
        "receiver__username",
        "group__name",
        "content",
    )
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    list_select_related = ("sender", "receiver", "group")
    readonly_fields = (
        "sender",
        "receiver",
        "group",
        "content",
        "attachment",
        "edited_at",
        "deleted_at",
        "is_read",
        "created_at",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(GroupConversation)
class GroupConversationAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "created_by", "created_at", "member_count")
    list_filter = ("created_at",)
    search_fields = ("name", "created_by__username")
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    list_select_related = ("created_by",)
    readonly_fields = ("name", "avatar", "created_by", "created_at")

    @admin.display(description="Members")
    def member_count(self, obj):
        return obj.memberships.count()

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(GroupMembership)
class GroupMembershipAdmin(admin.ModelAdmin):
    list_display = ("id", "group", "user", "role", "muted", "archived")
    list_filter = ("role", "muted", "archived")
    search_fields = ("group__name", "user__username")
    list_select_related = ("group", "user")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

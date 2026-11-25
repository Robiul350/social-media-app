from django.contrib import admin
from django.contrib.admin.models import LogEntry
from django.contrib.auth.admin import UserAdmin
from django.utils import timezone
from django.utils.html import format_html

from .models import User, Profile, Story, StoryView, StoryReaction


@admin.action(description="Deactivate selected users")
def deactivate_users(modeladmin, request, queryset):
    targets = queryset.exclude(pk=request.user.pk)
    for user in targets:
        user.is_active = False
        user.save(update_fields=["is_active"])
        modeladmin.log_change(request, user, "Deactivated via admin action")
    modeladmin.message_user(request, f"Deactivated {targets.count()} user(s).")


@admin.action(description="Reactivate selected users")
def reactivate_users(modeladmin, request, queryset):
    targets = queryset.exclude(pk=request.user.pk)
    for user in targets:
        user.is_active = True
        user.save(update_fields=["is_active"])
        modeladmin.log_change(request, user, "Reactivated via admin action")
    modeladmin.message_user(request, f"Reactivated {targets.count()} user(s).")


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        "id",
        "username",
        "email",
        "first_name",
        "last_name",
        "profile_thumbnail",
        "is_staff",
        "is_active",
        "date_joined",
        "last_login",
    )
    actions = (deactivate_users, reactivate_users)
    list_filter = ("is_active", "is_staff", "is_superuser", "date_joined")
    search_fields = ("username", "email", "first_name", "last_name")
    ordering = ("-date_joined",)
    date_hierarchy = "date_joined"
    list_select_related = ("profile",)

    @admin.display(description="Avatar")
    def profile_thumbnail(self, obj):
        profile = getattr(obj, "profile", None)
        if not profile or not profile.profile_picture:
            return "-"
        return format_html(
            '<img src="{}" class="sc-admin-avatar" alt="">',
            profile.profile_picture.url,
        )


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "profile_thumbnail", "location", "website", "updated_at")
    search_fields = ("user__username", "user__email", "bio", "location")
    list_filter = ("created_at", "updated_at")
    ordering = ("-updated_at",)
    list_select_related = ("user",)
    readonly_fields = ("profile_image_preview", "cover_image_preview", "created_at", "updated_at")
    fields = (
        "user", "profile_picture", "profile_image_preview", "cover_photo",
        "cover_image_preview", "bio", "location", "website", "date_of_birth",
        "created_at", "updated_at",
    )

    @admin.display(description="Profile picture")
    def profile_thumbnail(self, obj):
        if not obj.profile_picture:
            return "-"
        return format_html(
            '<img src="{}" class="sc-admin-avatar" alt="">',
            obj.profile_picture.url,
        )

    @admin.display(description="Profile picture preview")
    def profile_image_preview(self, obj):
        if not obj or not obj.profile_picture:
            return "No profile picture"
        return format_html(
            '<img src="{}" class="sc-admin-image-preview" alt="Profile picture">',
            obj.profile_picture.url,
        )

    @admin.display(description="Cover photo preview")
    def cover_image_preview(self, obj):
        if not obj or not obj.cover_photo:
            return "No cover photo"
        return format_html(
            '<img src="{}" class="sc-admin-cover-preview" alt="Cover photo">',
            obj.cover_photo.url,
        )


@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "author",
        "privacy",
        "created_at",
        "expires_at",
        "is_expired",
    )
    list_filter = ("privacy", "created_at", "expires_at")
    search_fields = ("author__username", "text")
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    list_select_related = ("author", "author__profile")
    readonly_fields = ("created_at", "story_preview")

    @admin.display(description="Status", boolean=True)
    def is_expired(self, obj):
        return obj.expires_at <= timezone.now()

    @admin.display(description="Media preview")
    def story_preview(self, obj):
        if not obj or not obj.media:
            return "No media attached"
        return format_html(
            '<a href="{}" target="_blank" rel="noopener">Open story media</a>',
            obj.media.url,
        )


@admin.register(StoryView)
class StoryViewAdmin(admin.ModelAdmin):
    list_display = ("id", "story", "viewer", "viewed_at")
    list_filter = ("viewed_at",)
    search_fields = ("story__author__username", "viewer__username")
    date_hierarchy = "viewed_at"
    ordering = ("-viewed_at",)
    list_select_related = ("story", "story__author", "viewer")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(StoryReaction)
class StoryReactionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "story", "reaction_type", "created_at")
    list_filter = ("reaction_type", "created_at")
    search_fields = ("user__username", "story__author__username")
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    list_select_related = ("user", "story", "story__author")

    def has_add_permission(self, request):
        return False


@admin.register(LogEntry)
class AdminLogEntryAdmin(admin.ModelAdmin):
    list_display = (
        "action_time",
        "user",
        "content_type",
        "object_repr",
        "action_flag",
    )
    list_filter = ("action_time", "action_flag", "content_type")
    search_fields = ("user__username", "object_repr", "change_message")
    date_hierarchy = "action_time"
    ordering = ("-action_time",)
    list_select_related = ("user", "content_type")
    readonly_fields = (
        "action_time",
        "user",
        "content_type",
        "object_id",
        "object_repr",
        "action_flag",
        "change_message",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

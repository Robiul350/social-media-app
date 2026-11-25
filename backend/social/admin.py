
from django.contrib import admin
from .models import Block, Comment, Follow, FriendRequest, Like



@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ("id", "post", "user", "created_at")
    list_filter = ("created_at",)
    search_fields = ("post__content", "user__username", "post__author__username")
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    list_select_related = ("post", "user", "post__author")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        "id", "post", "user", "parent", "created_at"
    )
    list_filter = ("created_at",)
    search_fields = ("content", "user__username", "post__content")
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    list_select_related = ("post", "user", "parent")
    readonly_fields = ("created_at", "updated_at")

@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ("id", "follower", "following", "created_at")
    list_filter = ("created_at",)
    search_fields = (
        "follower__username",
        "following__username",
        "follower__email",
        "following__email",
    )
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    list_select_related = ("follower", "following")


@admin.register(Block)
class BlockAdmin(admin.ModelAdmin):
    list_display = ("id", "blocker", "blocked", "created_at")
    list_filter = ("created_at",)
    search_fields = ("blocker__username", "blocked__username")
    ordering = ("-created_at",)
    list_select_related = ("blocker", "blocked")


@admin.register(FriendRequest)
class FriendRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "sender", "receiver", "status", "created_at", "updated_at")
    list_filter = ("status", "created_at")
    search_fields = ("sender__username", "receiver__username")
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    list_select_related = ("sender", "receiver")
    readonly_fields = ("created_at", "updated_at")

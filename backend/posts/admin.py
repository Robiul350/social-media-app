from django.contrib import admin
from django.utils.html import format_html

from .models import Post, PostReport


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "author",
        "content_preview",
        "media_preview",
        "created_at",
        "updated_at",
    )
    list_filter = ("created_at", "updated_at")
    search_fields = ("content", "author__username", "author__email")
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    list_select_related = ("author",)
    readonly_fields = ("media_detail_preview", "created_at", "updated_at")
    fields = ("author", "content", "image", "video", "media_detail_preview", "created_at", "updated_at")

    @admin.display(description="Content")
    def content_preview(self, obj):
        content = obj.content or ""
        return f"{content[:90]}{'...' if len(content) > 90 else ''}" or "Media post"

    @admin.display(description="Media")
    def media_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" class="sc-admin-media-thumb" alt="Post image">',
                obj.image.url,
            )
        if obj.video:
            return format_html(
                '<a href="{}" target="_blank" rel="noopener">View video</a>',
                obj.video.url,
            )
        return "-"

    @admin.display(description="Media preview")
    def media_detail_preview(self, obj):
        if not obj:
            return "Save the post before previewing media."
        if obj.image:
            return format_html(
                '<img src="{}" class="sc-admin-image-preview" alt="Post image">',
                obj.image.url,
            )
        if obj.video:
            return format_html(
                '<video class="sc-admin-video-preview" controls src="{}"></video>',
                obj.video.url,
            )
        return "No media attached"


@admin.register(PostReport)
class PostReportAdmin(admin.ModelAdmin):
    list_display = ("id", "post_link", "reporter", "reason_preview", "created_at")
    list_filter = ("created_at",)
    search_fields = (
        "reason",
        "reporter__username",
        "post__content",
        "post__author__username",
    )
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    list_select_related = ("post", "reporter", "post__author")
    readonly_fields = ("post", "reporter", "reason", "created_at")

    @admin.display(description="Post")
    def post_link(self, obj):
        return f"#{obj.post_id} — {obj.post.author.username}"

    @admin.display(description="Reason")
    def reason_preview(self, obj):
        return obj.reason[:90]

from rest_framework import serializers
from .models import Post


class PostSerializer(serializers.ModelSerializer):
    author_id = serializers.IntegerField(read_only=True)
    author_username = serializers.CharField(
        source="author.username",
        read_only=True
    )
    author_full_name = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    share_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    author_first_name = serializers.CharField(
        source="author.first_name",
        read_only=True
    )
    author_last_name = serializers.CharField(
        source="author.last_name",
        read_only=True
    )
    author_profile_picture = serializers.SerializerMethodField()
    is_bookmarked = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            "id",
            "author",
            "author_id",
            "author_username",
            "author_full_name",
            "author_first_name",
            "author_last_name",
            "author_profile_picture",
            "content",
            "image",
            "video",
            "audience",
            "is_draft",
            "is_pinned",
            "scheduled_for",
            "repost_of",
            "images",
            "is_bookmarked",
            "like_count",
            "comment_count",
            "share_count",
            "is_liked",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "author",
            "repost_of",
            "created_at",
            "updated_at",
        ]

    def get_like_count(self, obj):
        return obj.total_likes if hasattr(obj, "total_likes") else obj.likes.count()

    def get_comment_count(self, obj):
        return obj.total_comments if hasattr(obj, "total_comments") else obj.comments.count()

    def get_share_count(self, obj):
        return obj.total_shares if hasattr(obj, "total_shares") else obj.reposts.count()

    def get_author_full_name(self, obj):
        full_name = f"{obj.author.first_name} {obj.author.last_name}".strip()
        return full_name or obj.author.username

    def get_is_liked(self, obj):
        request = self.context.get("request")

        if request and request.user.is_authenticated:
            prefetched_likes = getattr(obj, "_viewer_likes", None)
            if prefetched_likes is not None:
                return bool(prefetched_likes)
            return obj.likes.filter(user=request.user).exists()

        return False

    def get_is_bookmarked(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False
        prefetched_bookmarks = getattr(obj, "_viewer_bookmarks", None)
        if prefetched_bookmarks is not None:
            return bool(prefetched_bookmarks)
        return obj.bookmarks.filter(user=request.user).exists()

    def get_images(self, obj):
        request = self.context.get("request")
        return [
            request.build_absolute_uri(item.image.url) if request else item.image.url
            for item in obj.images.all()
        ]

    def get_author_profile_picture(self, obj):
        profile = getattr(obj.author, "profile", None)
        if not profile or not profile.profile_picture:
            return None
        request = self.context.get("request")
        url = profile.profile_picture.url
        return request.build_absolute_uri(url) if request else url

    def validate(self, attrs):
        content = attrs.get(
            "content",
            self.instance.content if self.instance else "",
        )
        image = attrs.get("image", self.instance.image if self.instance else None)
        video = attrs.get("video", self.instance.video if self.instance else None)
        if not (content or "").strip() and not image and not video:
            raise serializers.ValidationError({
                "content": "Add text or media before publishing a post.",
            })
        return attrs

    def validate_image(self, value):
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError("Image files must be 10 MB or smaller.")
        if not value.content_type.startswith("image/"):
            raise serializers.ValidationError("Only image files are allowed.")
        return value

    def validate_video(self, value):
        if value.size > 100 * 1024 * 1024:
            raise serializers.ValidationError("Video files must be 100 MB or smaller.")
        if not value.content_type.startswith("video/"):
            raise serializers.ValidationError("Only video files are allowed.")
        return value

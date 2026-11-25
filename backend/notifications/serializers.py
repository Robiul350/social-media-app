
from rest_framework import serializers

from social.access import blocked_user_ids, visible_posts
from social.models import Comment

from .models import Notification, NotificationPreference


class NotificationSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(
        source="sender.username",
        read_only=True
    )
    post = serializers.SerializerMethodField()
    comment = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = [
            "id",
            "sender",
            "sender_username",
            "notification_type",
            "post",
            "comment",
            "is_read",
            "created_at",
        ]
        read_only_fields = fields

    def get_post(self, obj):
        if not obj.post_id:
            return None
        request = self.context.get("request")
        if not request or not visible_posts(request.user).filter(pk=obj.post_id).exists():
            return None
        return obj.post_id

    def get_comment(self, obj):
        if not obj.comment_id:
            return None
        request = self.context.get("request")
        if not request:
            return None
        visible = Comment.objects.filter(
            pk=obj.comment_id,
            post__in=visible_posts(request.user),
        ).exclude(user_id__in=blocked_user_ids(request.user)).exists()
        return obj.comment_id if visible else None


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationPreference
        fields = ["likes", "comments", "replies", "follows", "friend_requests", "messages", "mentions", "story_reactions"]

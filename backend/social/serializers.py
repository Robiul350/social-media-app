
from rest_framework import serializers

from .models import Comment, FriendRequest


class CommentSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        source="user.username",
        read_only=True
    )
    profile_picture = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            "id",
            "post",
            "user",
            "username",
            "profile_picture",
            "content",
            "parent",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "post",
            "user",
            "created_at",
            "updated_at",
        ]

    def validate_parent(self, parent):
        if parent and parent.post_id != self.context["post_id"]:
            raise serializers.ValidationError(
                "Reply must belong to the same post."
            )
        if self.instance and (parent.pk if parent else None) != self.instance.parent_id:
            raise serializers.ValidationError(
                "A comment's reply parent cannot be changed."
            )
        return parent

    def get_profile_picture(self, obj):
        profile = getattr(obj.user, "profile", None)
        if not profile or not profile.profile_picture:
            return None

        url = profile.profile_picture.url
        request = self.context.get("request")
        return request.build_absolute_uri(url) if request else url



from django.contrib.auth import get_user_model

User = get_user_model()


class UserSummarySerializer(serializers.ModelSerializer):
    profile_picture = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "profile_picture",
        ]

    def get_profile_picture(self, obj):
        profile = getattr(obj, "profile", None)
        if not profile or not profile.profile_picture:
            return None

        url = profile.profile_picture.url
        request = self.context.get("request")
        return request.build_absolute_uri(url) if request else url


class FriendRequestSerializer(serializers.ModelSerializer):
    sender = UserSummarySerializer(read_only=True)
    receiver = UserSummarySerializer(read_only=True)

    class Meta:
        model = FriendRequest
        fields = ["id", "sender", "receiver", "status", "created_at", "updated_at"]
        read_only_fields = fields

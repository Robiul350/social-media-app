
from rest_framework import serializers
from .models import Message, GroupConversation


class MessageSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(
        source="sender.username",
        read_only=True
    )
    receiver_username = serializers.CharField(
        source="receiver.username",
        read_only=True
    )

    class Meta:
        model = Message
        fields = [
            "id",
            "sender",
            "sender_username",
            "receiver",
            "receiver_username",
            "content",
            "attachment",
            "edited_at",
            "deleted_at",
            "is_read",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "sender",
            "sender_username",
            "receiver",
            "receiver_username",
            "is_read",
            "created_at",
        ]

    def validate_content(self, value):
        if not value.strip():
            raise serializers.ValidationError(
                "Message cannot be empty."
            )
        return value

    def validate_attachment(self, value):
        if not value:
            return value
        allowed_prefixes = (
            "image/",
            "video/",
            "audio/",
            "application/pdf",
            "text/plain",
        )
        content_type = (getattr(value, "content_type", "") or "").lower()
        if not content_type.startswith(allowed_prefixes):
            raise serializers.ValidationError(
                "Only images, videos, audio, PDF, and text files are allowed."
            )
        if value.size > 25 * 1024 * 1024:
            raise serializers.ValidationError(
                "Chat attachments must be 25 MB or smaller."
            )
        return value


class GroupConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupConversation
        fields = ["id", "name", "avatar", "created_by", "created_at"]
        read_only_fields = ["id", "created_by", "created_at"]

    def validate_avatar(self, value):
        if not value:
            return value
        content_type = (getattr(value, "content_type", "") or "").lower()
        if not content_type.startswith("image/"):
            raise serializers.ValidationError("Only image files are allowed.")
        if value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("Group avatars must be 5 MB or smaller.")
        return value

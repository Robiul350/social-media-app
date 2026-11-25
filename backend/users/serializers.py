
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.db.models import Q
from rest_framework import serializers

from .models import User, Profile, Story, StoryView, StoryReaction
from social.models import Block, Follow, FriendRequest
from social.access import can_message_user, can_view_profile
from posts.models import Post


# =========================
# Registration Serializer
# =========================

class RegisterSerializer(serializers.ModelSerializer):

    password = serializers.CharField(
        write_only=True,
        min_length=8
    )

    password2 = serializers.CharField(
        write_only=True
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password",
            "password2"
        ]

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "Email already exists."
            )
        return value

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                "Username already exists."
            )
        return value

    def validate(self, data):
        if data["password"] != data["password2"]:
            raise serializers.ValidationError(
                {"password2": "Passwords do not match."}
            )
        try:
            validate_password(data["password"])
        except DjangoValidationError as exc:
            raise serializers.ValidationError({"password": list(exc.messages)})

        return data

    def create(self, validated_data):
        validated_data.pop("password2")

        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"]
        )

        return user


# =========================
# Login Serializer
# =========================

class LoginSerializer(serializers.Serializer):

    username = serializers.CharField()
    password = serializers.CharField(
        write_only=True
    )

    def validate(self, data):

        username = data["username"].strip()
        password = data["password"]

        user = authenticate(
            username=username,
            password=password
        )

        if user is None:
            raise serializers.ValidationError(
                "Invalid username or password."
            )

        if not user.is_active:
            raise serializers.ValidationError(
                "User account is inactive."
            )

        data["user"] = user

        return data


# =========================
# Profile Serializer
# =========================

class ProfileSerializer(serializers.ModelSerializer):
    remove_profile_picture = serializers.BooleanField(
        write_only=True,
        required=False,
        default=False,
    )
    remove_cover_photo = serializers.BooleanField(
        write_only=True,
        required=False,
        default=False,
    )

    class Meta:
        model = Profile
        fields = [
            "id",
            "user",
            "profile_picture",
            "cover_photo",
            "bio",
            "location",
            "website",
            "date_of_birth",
            "is_private",
            "allow_comments",
            "allow_messages",
            "is_verified",
            "social_links",
            "education",
            "work",
            "created_at",
            "updated_at",
            "remove_profile_picture",
            "remove_cover_photo",
        ]
        read_only_fields = ["user", "is_verified"]

    def update(self, instance, validated_data):
        replaced_files = []
        for field_name, remove_field in (
            ("profile_picture", "remove_profile_picture"),
            ("cover_photo", "remove_cover_photo"),
        ):
            remove_file = validated_data.pop(remove_field, False)
            current_file = getattr(instance, field_name)
            if remove_file:
                validated_data[field_name] = None

            if current_file and (
                remove_file
                or (
                    field_name in validated_data
                    and validated_data[field_name] is not current_file
                )
            ):
                replaced_files.append((current_file.storage, current_file.name))

        updated_instance = super().update(instance, validated_data)
        for storage, name in replaced_files:
            transaction.on_commit(lambda storage=storage, name=name: storage.delete(name))
        return updated_instance

    def validate_profile_picture(self, value):
        if value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("Profile pictures must be 5 MB or smaller.")
        if not value.content_type.startswith("image/"):
            raise serializers.ValidationError("Only image files are allowed.")
        return value

    def validate_cover_photo(self, value):
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError("Cover photos must be 10 MB or smaller.")
        if not value.content_type.startswith("image/"):
            raise serializers.ValidationError("Only image files are allowed.")
        return value


class PublicProfileDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = [
            "profile_picture",
            "cover_photo",
            "bio",
            "location",
            "website",
        ]


class StorySerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source="author.username", read_only=True)
    reaction_counts = serializers.SerializerMethodField()
    total_reactions = serializers.SerializerMethodField()
    user_reaction = serializers.SerializerMethodField()

    class Meta:
        model = Story
        fields = [
            "id",
            "author",
            "author_username",
            "media",
            "text",
            "privacy",
            "expires_at",
            "created_at",
            "reaction_counts",
            "total_reactions",
            "user_reaction",
        ]
        # The API sets the 24-hour expiry when saving, so clients must not
        # provide it when creating a story.
        read_only_fields = ["author", "created_at", "expires_at"]

    def validate_media(self, value):
        allowed_prefixes = ("image/", "video/")
        content_type = (getattr(value, "content_type", "") or "").lower()
        if not content_type.startswith(allowed_prefixes):
            raise serializers.ValidationError("Only image or video files are allowed.")
        if value.size > 25 * 1024 * 1024:
            raise serializers.ValidationError("Story media must be 25 MB or smaller.")
        return value

    def validate(self, attrs):
        if not attrs.get("media") and not str(attrs.get("text") or "").strip():
            raise serializers.ValidationError("Add a photo, video, or a short message.")
        return attrs

    def get_reaction_counts(self, obj):
        request = self.context.get("request")
        counts = {}
        for choice in StoryReaction.ReactionType.choices:
            counts[choice[0]] = 0
        if hasattr(obj, "_reaction_counts"):
            for reaction_type, count in obj._reaction_counts.items():
                counts[reaction_type] = count
        else:
            for reaction in obj.reactions.all():
                counts[reaction.reaction_type] = counts.get(reaction.reaction_type, 0) + 1
        return counts

    def get_total_reactions(self, obj):
        if hasattr(obj, "_total_reactions"):
            return obj._total_reactions
        return obj.reactions.count()

    def get_user_reaction(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return None
        if hasattr(obj, "_user_reaction"):
            return obj._user_reaction
        reaction = obj.reactions.filter(user=request.user).first()
        return reaction.reaction_type if reaction else None


class StoryReactionSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)
    reaction_emoji = serializers.SerializerMethodField()

    class Meta:
        model = StoryReaction
        fields = ["id", "user_id", "username", "reaction_type", "reaction_emoji", "created_at", "updated_at"]
        read_only_fields = ["user", "story", "created_at", "updated_at"]

    def get_reaction_emoji(self, obj):
        emoji_map = {
            StoryReaction.ReactionType.LIKE: "👍",
            StoryReaction.ReactionType.LOVE: "❤️",
            StoryReaction.ReactionType.CARE: "🥰",
            StoryReaction.ReactionType.HAHA: "😂",
            StoryReaction.ReactionType.WOW: "😮",
            StoryReaction.ReactionType.SAD: "😢",
            StoryReaction.ReactionType.ANGRY: "😡",
        }
        return emoji_map.get(obj.reaction_type, "")


# =========================
# Public Profile Serializer
# =========================

class PublicProfileSerializer(serializers.ModelSerializer):

    profile = serializers.SerializerMethodField()

    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    posts_count = serializers.SerializerMethodField()

    is_following = serializers.SerializerMethodField()
    follows_you = serializers.SerializerMethodField()
    friendship_status = serializers.SerializerMethodField()
    friend_request_id = serializers.SerializerMethodField()
    is_private = serializers.SerializerMethodField()
    can_view_profile = serializers.SerializerMethodField()
    can_message = serializers.SerializerMethodField()
    is_blocked = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "profile",
            "followers_count",
            "following_count",
            "posts_count",
            "is_following",
            "follows_you",
            "friendship_status",
            "friend_request_id",
            "is_private",
            "can_view_profile",
            "can_message",
            "is_blocked",
        ]

    def get_profile(self, obj):
        if not can_view_profile(self.context.get("request").user, obj):
            return None
        return PublicProfileDetailsSerializer(
            obj.profile,
            context=self.context,
        ).data

    def get_is_private(self, obj):
        profile = getattr(obj, "profile", None)
        return bool(profile and profile.is_private)

    def get_can_view_profile(self, obj):
        request = self.context.get("request")
        return bool(request and can_view_profile(request.user, obj))

    def get_is_blocked(self, obj):
        request = self.context.get("request")
        return bool(
            request
            and request.user.is_authenticated
            and Block.objects.filter(blocker=request.user, blocked=obj).exists()
        )

    def get_can_message(self, obj):
        request = self.context.get("request")
        return bool(
            request
            and request.user.is_authenticated
            and can_message_user(request.user, obj)
            and can_message_user(obj, request.user)
        )

    def _friend_request_for(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return None

        cache = self.context.setdefault("_friend_request_cache", {})
        if obj.id not in cache:
            cache[obj.id] = FriendRequest.objects.filter(
                Q(sender=request.user, receiver=obj)
                | Q(sender=obj, receiver=request.user)
            ).first()
        return cache[obj.id]

    def get_followers_count(self, obj):
        return Follow.objects.filter(
            following=obj
        ).count()

    def get_following_count(self, obj):
        return Follow.objects.filter(
            follower=obj
        ).count()

    def get_posts_count(self, obj):
        request = self.context.get("request")
        if request and not can_view_profile(request.user, obj):
            return 0
        return Post.objects.filter(
            author=obj
        ).count()

    def get_is_following(self, obj):
        request = self.context.get("request")

        if request and request.user.is_authenticated:
            return Follow.objects.filter(
                follower=request.user,
                following=obj
            ).exists()

        return False

    def get_follows_you(self, obj):
        request = self.context.get("request")

        if request and request.user.is_authenticated:
            return Follow.objects.filter(
                follower=obj,
                following=request.user
            ).exists()

        return False

    def get_friendship_status(self, obj):
        friend_request = self._friend_request_for(obj)
        if not friend_request:
            return "none"
        if friend_request.status == FriendRequest.Status.ACCEPTED:
            return "friends"
        if friend_request.status == FriendRequest.Status.PENDING:
            request = self.context["request"]
            return (
                "outgoing_pending"
                if friend_request.sender_id == request.user.id
                else "incoming_pending"
            )
        return "none"

    def get_friend_request_id(self, obj):
        friend_request = self._friend_request_for(obj)
        if friend_request and friend_request.status == FriendRequest.Status.PENDING:
            return friend_request.id
        return None

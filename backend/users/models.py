from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user model with email-based authentication."""

    email = models.EmailField(unique=True)
    email_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.username


class Profile(models.Model):
    class AccessLevel(models.TextChoices):
        EVERYONE = "everyone", "Everyone"
        FOLLOWERS = "followers", "Followers"
        FRIENDS = "friends", "Friends"
        NOBODY = "nobody", "Nobody"

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile"
    )

    profile_picture = models.ImageField(
        upload_to="profile/",
        blank=True,
        null=True
    )

    cover_photo = models.ImageField(
        upload_to="cover/",
        blank=True,
        null=True
    )

    bio = models.TextField(
        blank=True,
        null=True
    )

    location = models.CharField(
        max_length=150,
        blank=True,
        null=True
    )

    website = models.URLField(
        blank=True,
        null=True
    )

    date_of_birth = models.DateField(
        blank=True,
        null=True
    )

    is_private = models.BooleanField(default=False)
    allow_comments = models.CharField(
        max_length=10,
        choices=AccessLevel.choices,
        default=AccessLevel.EVERYONE,
    )
    allow_messages = models.CharField(
        max_length=10,
        choices=AccessLevel.choices,
        default=AccessLevel.EVERYONE,
    )
    is_verified = models.BooleanField(default=False)
    social_links = models.JSONField(default=dict, blank=True)
    education = models.CharField(max_length=250, blank=True, default="")
    work = models.CharField(max_length=250, blank=True, default="")

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.user.username}'s Profile"


class Story(models.Model):
    class Privacy(models.TextChoices):
        PUBLIC = "public", "Public"
        FOLLOWERS = "followers", "Followers"
        FRIENDS = "friends", "Friends"

    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="stories")
    media = models.FileField(upload_to="stories/", blank=True, null=True)
    text = models.CharField(max_length=500, blank=True, default="")
    privacy = models.CharField(max_length=10, choices=Privacy.choices, default=Privacy.PUBLIC)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    viewers = models.ManyToManyField(User, related_name="viewed_stories", through="StoryView", blank=True)

    class Meta:
        ordering = ["-created_at"]


class StoryView(models.Model):
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name="story_views")
    viewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="story_views")
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["story", "viewer"], name="unique_story_view")]


# This model already has an applied migration (0006_adminaction). Importing it
# keeps Django's model state aligned with the existing database table without
# creating or deleting any schema. It is not used as an audit source because it
# has no actor field and no code writes to it.
from .admin_action import AdminAction  # noqa: E402,F401


class StoryReaction(models.Model):
    """A reaction a user adds to a story (Facebook-style emoji reactions)."""

    class ReactionType(models.TextChoices):
        LIKE = "like", "Like 👍"
        LOVE = "love", "Love ❤️"
        CARE = "care", "Care 🥰"
        HAHA = "haha", "Haha 😂"
        WOW = "wow", "Wow 😮"
        SAD = "sad", "Sad 😢"
        ANGRY = "angry", "Angry 😡"

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="story_reactions",
    )
    story = models.ForeignKey(
        Story,
        on_delete=models.CASCADE,
        related_name="reactions",
    )
    reaction_type = models.CharField(
        max_length=10,
        choices=ReactionType.choices,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "story"],
                name="unique_user_story_reaction",
            ),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} reacted {self.reaction_type} to story {self.story.id}"
from django.db import models
from django.conf import settings


class Post(models.Model):
    class Audience(models.TextChoices):
        PUBLIC = "public", "Public"
        FOLLOWERS = "followers", "Followers"
        FRIENDS = "friends", "Friends"

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="posts"
    )

    content = models.TextField(
        blank=True,
        null=True
    )

    image = models.ImageField(
        upload_to="posts/images/",
        blank=True,
        null=True
    )

    video = models.FileField(
        upload_to="posts/videos/",
        blank=True,
        null=True
    )
    audience = models.CharField(max_length=10, choices=Audience.choices, default=Audience.PUBLIC)
    is_draft = models.BooleanField(default=False)
    is_pinned = models.BooleanField(default=False)
    scheduled_for = models.DateTimeField(blank=True, null=True)
    repost_of = models.ForeignKey("self", on_delete=models.SET_NULL, blank=True, null=True, related_name="reposts")

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.author.username}'s Post"


class PostImage(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="posts/images/")
    position = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["position"]


class Bookmark(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="bookmarks")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bookmarks")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["post", "user"], name="unique_post_bookmark")]


class Poll(models.Model):
    post = models.OneToOneField(Post, on_delete=models.CASCADE, related_name="poll")
    question = models.CharField(max_length=250)
    expires_at = models.DateTimeField(blank=True, null=True)


class PollOption(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name="options")
    text = models.CharField(max_length=120)


class PollVote(models.Model):
    option = models.ForeignKey(PollOption, on_delete=models.CASCADE, related_name="votes")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="poll_votes")

    class Meta:
        constraints = [models.UniqueConstraint(fields=["option", "user"], name="unique_poll_vote_option")]


class Hashtag(models.Model):
    name = models.CharField(max_length=100, unique=True)
    posts = models.ManyToManyField(Post, related_name="hashtags", blank=True)


class PostReport(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="reports")
    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="post_reports")
    reason = models.CharField(max_length=250)
    created_at = models.DateTimeField(auto_now_add=True)
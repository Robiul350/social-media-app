from django.db.models import Count, Prefetch, Q
from django.utils import timezone

from posts.models import Bookmark, Post

from .models import Block, Follow, FriendRequest, Like


def is_blocked_between(first, second):
    first_id = getattr(first, "pk", first)
    second_id = getattr(second, "pk", second)
    return Block.objects.filter(
        Q(blocker_id=first_id, blocked_id=second_id)
        | Q(blocker_id=second_id, blocked_id=first_id)
    ).exists()


def blocked_user_ids(user):
    relationships = Block.objects.filter(
        Q(blocker=user) | Q(blocked=user)
    ).values_list("blocker_id", "blocked_id")
    return {
        second_id if first_id == user.id else first_id
        for first_id, second_id in relationships
    }


def friend_ids(user):
    relationships = FriendRequest.objects.filter(
        Q(sender=user) | Q(receiver=user),
        status=FriendRequest.Status.ACCEPTED,
    ).values_list("sender_id", "receiver_id")
    return {
        second_id if first_id == user.id else first_id
        for first_id, second_id in relationships
    }


def can_view_profile(viewer, target):
    if not viewer or not viewer.is_authenticated:
        return False
    if viewer.pk == target.pk:
        return True
    if is_blocked_between(viewer, target):
        return False
    profile = getattr(target, "profile", None)
    return not profile or not profile.is_private or target.pk in friend_ids(viewer)


def _allows_interaction(actor, target, setting_name):
    if not actor or not actor.is_authenticated or is_blocked_between(actor, target):
        return False
    if actor.pk == target.pk:
        return True

    profile = getattr(target, "profile", None)
    if not profile:
        return False
    if profile.is_private and target.pk not in friend_ids(actor):
        return False

    policy = getattr(profile, setting_name)
    if policy == "everyone":
        return True
    if policy == "followers":
        return Follow.objects.filter(follower=actor, following=target).exists()
    if policy == "friends":
        return target.pk in friend_ids(actor)
    return False


def can_comment_on_profile(actor, target):
    return _allows_interaction(actor, target, "allow_comments")


def can_message_user(sender, receiver):
    return _allows_interaction(sender, receiver, "allow_messages")


def can_chat_between(first, second):
    return (
        not is_blocked_between(first, second)
        and can_message_user(first, second)
        and can_message_user(second, first)
    )


def visible_posts(viewer):
    friends = friend_ids(viewer)
    followed = Follow.objects.filter(follower=viewer).values("following_id")
    published_posts = (
        Q(is_draft=False)
        & (Q(scheduled_for__isnull=True) | Q(scheduled_for__lte=timezone.now()))
        & (
            Q(audience=Post.Audience.PUBLIC)
            | Q(audience=Post.Audience.FOLLOWERS, author_id__in=followed)
            | Q(audience=Post.Audience.FRIENDS, author_id__in=friends)
        )
        & (
            Q(author__profile__isnull=True)
            | Q(author__profile__is_private=False)
            | Q(author_id__in=friends)
        )
    )
    own_published_posts = (
        Q(author_id=viewer.pk, is_draft=False)
        & (Q(scheduled_for__isnull=True) | Q(scheduled_for__lte=timezone.now()))
    )
    return (
        Post.objects.filter(
            own_published_posts | published_posts
        )
        .exclude(author_id__in=blocked_user_ids(viewer))
        .distinct()
    )


def posts_for_detail(viewer):
    """Visible posts plus all of the viewer's own posts (including drafts)."""
    return Post.objects.filter(
        Q(author_id=viewer.pk) | Q(pk__in=visible_posts(viewer).values("pk"))
    ).distinct()


def with_post_serializer_prefetches(viewer, queryset=None):
    """Apply the prefetches/annotations expected by PostSerializer."""
    base = queryset if queryset is not None else visible_posts(viewer)
    return (
        base.select_related("author", "author__profile")
        .prefetch_related(
            "images",
            Prefetch("likes", queryset=Like.objects.filter(user=viewer), to_attr="_viewer_likes"),
            Prefetch("bookmarks", queryset=Bookmark.objects.filter(user=viewer), to_attr="_viewer_bookmarks"),
        )
        .annotate(
            total_likes=Count("likes", distinct=True),
            total_comments=Count("comments", distinct=True),
            total_shares=Count("reposts", distinct=True),
        )
        .distinct()
    )

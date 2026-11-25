"""Real data helpers for the SocialConnect admin dashboard.

Every number produced here comes from an existing database field. Where the
schema cannot support a requested metric, the metric is marked unavailable
rather than estimated or invented.
"""

from datetime import datetime, time, timedelta

from django.db import connections, router
from django.db.models import Count, Q
from django.db.models.functions import TruncDate, TruncMonth
from django.utils import timezone
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken

from chat.models import Message
from notifications.models import Notification
from posts.models import Post, PostReport
from social.models import Comment, FriendRequest, Like
from users.models import Story, StoryReaction, User


RANGE_OPTIONS = {
    7: "Last 7 days",
    30: "Last 30 days",
    90: "Last 90 days",
}


def normalize_range(value):
    try:
        days = int(value)
    except (TypeError, ValueError):
        return 30
    return days if days in RANGE_OPTIONS else 30


def analytics_bounds(days):
    end = timezone.now()
    return end - timedelta(days=days), end


def daily_labels(start, end):
    days = (end.date() - start.date()).days
    return [
        (start + timedelta(days=offset)).date().isoformat()
        for offset in range(days + 1)
    ]


def _local_day(value):
    if timezone.is_aware(value):
        return timezone.localtime(value).date().isoformat()
    return value.date().isoformat()


def daily_counts(queryset, date_field, labels, start, end):
    rows = (
        queryset.filter(
            **{
                f"{date_field}__gte": start,
                f"{date_field}__lt": end,
            }
        )
        .annotate(day=TruncDate(date_field))
        .values("day")
        .annotate(total=Count("pk"))
    )
    totals = {row["day"].isoformat(): row["total"] for row in rows if row["day"]}
    return [totals.get(label, 0) for label in labels]


def cumulative(values):
    total = 0
    result = []
    for value in values:
        total += value
        result.append(total)
    return result


def daily_distinct_users(queryset, date_field, labels, start, end):
    rows = queryset.filter(
        **{
            f"{date_field}__gte": start,
            f"{date_field}__lt": end,
        }
    ).values_list(date_field, "user_id")
    by_day = {label: set() for label in labels}
    for timestamp, user_id in rows:
        if not user_id:
            continue
        label = _local_day(timestamp)
        if label in by_day:
            by_day[label].add(user_id)
    return [len(by_day[label]) for label in labels]


def monthly_labels(months=6):
    current = timezone.localdate().replace(day=1)
    result = []
    for offset in range(months - 1, -1, -1):
        month_number = current.month - offset
        year = current.year
        while month_number <= 0:
            month_number += 12
            year -= 1
        result.append(current.replace(year=year, month=month_number))
    return result


def monthly_counts(queryset, date_field, months):
    month_indexes = {month.strftime("%Y-%m"): index for index, month in enumerate(months)}
    values = [0] * len(months)
    rows = (
        queryset.annotate(month=TruncMonth(date_field))
        .values("month")
        .annotate(total=Count("pk"))
    )
    for row in rows:
        if not row["month"]:
            continue
        index = month_indexes.get(row["month"].strftime("%Y-%m"))
        if index is not None:
            values[index] = row["total"]
    return values


def monthly_distinct_users(months):
    labels = [month.strftime("%Y-%m") for month in months]
    by_month = {label: set() for label in labels}
    month_start = timezone.make_aware(datetime.combine(months[0], time.min))
    tokens = OutstandingToken.objects.filter(created_at__gte=month_start).values_list(
        "created_at", "user_id"
    )
    for timestamp, user_id in tokens:
        if not user_id:
            continue
        label = _local_day(timestamp)[:7]
        if label in by_month:
            by_month[label].add(user_id)
    return [len(by_month[label]) for label in labels]


def dashboard_series():
    months = monthly_labels()
    labels = [month.strftime("%b %Y") for month in months]
    return {
        "labels": labels,
        "users": monthly_counts(User.objects, "date_joined", months),
        "posts": monthly_counts(Post.objects, "created_at", months),
    }


TREND_DAYS = 30


def _relation_available(model):
    """Return True when a model's table exists in its configured database.

    Optional dashboard metrics can be skipped when their schema is missing.
    This check never swallows query errors: connection and permission failures
    still propagate to the caller.
    """
    alias = router.db_for_read(model)
    return model._meta.db_table in connections[alias].introspection.table_names()


def _trend(current, previous):
    delta = current - previous
    if delta > 0:
        return {
            "direction": "up",
            "label": f"+{delta} vs previous {TREND_DAYS}d",
        }
    if delta < 0:
        return {
            "direction": "down",
            "label": f"{delta} vs previous {TREND_DAYS}d",
        }
    return {
        "direction": "flat",
        "label": f"No change vs previous {TREND_DAYS}d",
    }


def _window_bounds():
    end = timezone.localtime()
    start = end - timedelta(days=TREND_DAYS)
    previous_start = start - timedelta(days=TREND_DAYS)
    return start, end, previous_start


def _count_in_window(queryset, field, start, end):
    return queryset.filter(
        **{f"{field}__gte": start, f"{field}__lt": end}
    ).count()


def _distinct_users_in_window(start, end):
    return (
        OutstandingToken.objects.filter(created_at__gte=start, created_at__lt=end)
        .values("user_id")
        .distinct()
        .count()
    )


def dashboard_kpis(permissions):
    start, end, previous_start = _window_bounds()
    story_reactions_available = _relation_available(StoryReaction)

    def value(allowed, queryset_count):
        return queryset_count() if allowed else "—"

    def trend(allowed, current, previous):
        return _trend(current, previous) if allowed else None

    new_users = _count_in_window(User.objects, "date_joined", start, end)
    previous_users = _count_in_window(
        User.objects, "date_joined", previous_start, start
    )
    active_users = _distinct_users_in_window(start, end)
    previous_active_users = _distinct_users_in_window(previous_start, start)
    new_posts = _count_in_window(Post.objects, "created_at", start, end)
    previous_posts = _count_in_window(Post.objects, "created_at", previous_start, start)
    new_comments = _count_in_window(Comment.objects, "created_at", start, end)
    previous_comments = _count_in_window(
        Comment.objects, "created_at", previous_start, start
    )
    new_likes = _count_in_window(Like.objects, "created_at", start, end)
    previous_likes = _count_in_window(Like.objects, "created_at", previous_start, start)
    new_requests = _count_in_window(FriendRequest.objects, "created_at", start, end)
    previous_requests = _count_in_window(
        FriendRequest.objects, "created_at", previous_start, start
    )
    new_reports = _count_in_window(PostReport.objects, "created_at", start, end)
    previous_reports = _count_in_window(
        PostReport.objects, "created_at", previous_start, start
    )

    cards = [
        {
            "label": "Total Users",
            "value": value(permissions["users"], User.objects.count),
            "description": "Registered accounts",
            "icon": "users",
            "accent": "blue",
            "permission": "users",
            "trend": trend(permissions["users"], new_users, previous_users),
        },
        {
            "label": "Active Users",
            "value": value(permissions["users"], lambda: active_users),
            "description": "Distinct users issued a refresh token in 30 days",
            "icon": "active-users",
            "accent": "teal",
            "permission": "users",
            "trend": trend(
                permissions["users"], active_users, previous_active_users
            ),
        },
        {
            "label": "Total Posts",
            "value": value(permissions["posts"], Post.objects.count),
            "description": "All published and draft posts",
            "icon": "posts",
            "accent": "violet",
            "permission": "posts",
            "trend": trend(permissions["posts"], new_posts, previous_posts),
        },
        {
            "label": "Total Comments",
            "value": value(permissions["comments"], Comment.objects.count),
            "description": "Top-level comments and replies",
            "icon": "comments",
            "accent": "amber",
            "permission": "comments",
            "trend": trend(permissions["comments"], new_comments, previous_comments),
        },
        {
            "label": "Pending Reports",
            "value": value(permissions["reports"], PostReport.objects.count),
            "description": "Submitted reports awaiting review; no status field exists",
            "icon": "reports",
            "accent": "amber",
            "permission": "reports",
            "trend": trend(permissions["reports"], new_reports, previous_reports),
        },
        {
            "label": "Total Likes",
            "value": value(permissions["likes"], Like.objects.count),
            "description": "Post reactions recorded",
            "icon": "likes",
            "accent": "violet",
            "permission": "likes",
            "trend": trend(permissions["likes"], new_likes, previous_likes),
        },
        {
            "label": "New Registrations",
            "value": value(permissions["users"], lambda: new_users),
            "description": f"Accounts created in the last {TREND_DAYS} days",
            "icon": "new-users",
            "accent": "teal",
            "permission": "users",
            "trend": trend(permissions["users"], new_users, previous_users),
        },
        {
            "label": "Friend Requests",
            "value": value(
                permissions["friend_requests"],
                lambda: FriendRequest.objects.filter(
                    status=FriendRequest.Status.PENDING
                ).count(),
            ),
            "description": "Pending right now",
            "icon": "requests",
            "accent": "amber",
            "permission": "friend_requests",
            "trend": trend(permissions["friend_requests"], new_requests, previous_requests),
        },
        {
            "label": "Total Stories",
            "value": value(permissions["stories"], Story.objects.count),
            "description": "All active and expired stories",
            "icon": "stories",
            "accent": "violet",
            "permission": "stories",
            "trend": None,
        },
        {
            "label": "Active Stories",
            "value": value(
                permissions["stories"],
                lambda: Story.objects.filter(expires_at__gt=timezone.now()).count(),
            ),
            "description": "Stories not yet expired",
            "icon": "stories",
            "accent": "teal",
            "permission": "stories",
            "trend": None,
        },
        {
            "label": "Expired Stories",
            "value": value(
                permissions["stories"],
                lambda: Story.objects.filter(expires_at__lte=timezone.now()).count(),
            ),
            "description": "Stories past their 24-hour expiry",
            "icon": "stories",
            "accent": "amber",
            "permission": "stories",
            "trend": None,
        },
        {
            "label": "Total Story Reactions",
            "value": value(
                permissions["story_reactions"] and story_reactions_available,
                StoryReaction.objects.count,
            ),
            "description": (
                "All story reactions recorded"
                if story_reactions_available
                else "Story reactions are not available in this database"
            ),
            "icon": "reactions",
            "accent": "blue",
            "permission": "story_reactions",
            "available": story_reactions_available,
            "trend": None,
        },
    ]

    return cards


def build_analytics(permissions, days):
    start, end = analytics_bounds(days)
    labels = daily_labels(start, end)
    story_reactions_available = _relation_available(StoryReaction)
    zeros = [0] * len(labels)

    def series(allowed, queryset, field):
        return daily_counts(queryset, field, labels, start, end) if allowed else zeros[:]

    registrations = series(permissions["users"], User.objects, "date_joined")
    registrations_cumulative = cumulative(registrations)
    active_users = (
        daily_distinct_users(OutstandingToken.objects, "created_at", labels, start, end)
        if permissions["users"]
        else zeros[:]
    )
    posts = series(permissions["posts"], Post.objects, "created_at")
    comments = series(permissions["comments"], Comment.objects, "created_at")
    likes = series(permissions["likes"], Like.objects, "created_at")
    messages = series(permissions["messages"], Message.objects, "created_at")
    notifications = series(permissions["notifications"], Notification.objects, "created_at")
    reports = series(permissions["reports"], PostReport.objects, "created_at")
    friend_requests_created = series(
        permissions["friend_requests"], FriendRequest.objects, "created_at"
    )
    friend_requests_accepted = (
        daily_counts(
            FriendRequest.objects.filter(status=FriendRequest.Status.ACCEPTED),
            "updated_at",
            labels,
            start,
            end,
        )
        if permissions["friend_requests"]
        else zeros[:]
    )

    months = monthly_labels()
    monthly_active = (
        monthly_distinct_users(months)
        if permissions["users"]
        else [0] * len(months)
    )

    popular_posts = []
    if permissions["posts"] and (permissions["likes"] or permissions["comments"]):
        annotations = {}
        if permissions["likes"]:
            annotations["engagement_likes"] = Count("likes", distinct=True)
        if permissions["comments"]:
            annotations["engagement_comments"] = Count("comments", distinct=True)
        order_fields = [
            f"-{field}" for field in ("engagement_likes", "engagement_comments")
            if field in annotations
        ]
        order_fields.append("-created_at")
        popular_posts = list(
            Post.objects.filter(created_at__gte=start, created_at__lte=end)
            .select_related("author", "author__profile")
            .annotate(**annotations)
            .order_by(*order_fields)[:5]
        )

    top_users = []
    if permissions["users"] and (
        permissions["posts"] or permissions["comments"] or permissions["likes"]
    ):
        annotations = {}
        if permissions["posts"]:
            annotations["activity_posts"] = Count(
                "posts",
                filter=Q(posts__created_at__gte=start, posts__created_at__lt=end),
                distinct=True,
            )
        if permissions["comments"]:
            annotations["activity_comments"] = Count(
                "user_comments",
                filter=Q(
                    user_comments__created_at__gte=start,
                    user_comments__created_at__lt=end,
                ),
                distinct=True,
            )
        if permissions["likes"]:
            annotations["activity_likes"] = Count(
                "post_likes",
                filter=Q(
                    post_likes__created_at__gte=start,
                    post_likes__created_at__lt=end,
                ),
                distinct=True,
            )
        order_fields = [
            f"-{field}" for field in ("activity_posts", "activity_comments", "activity_likes")
            if field in annotations
        ]
        order_fields.append("-date_joined")
        top_users = list(
            User.objects.filter(date_joined__lte=end)
            .annotate(**annotations)
            .order_by(*order_fields)[:5]
        )

    totals = {
        "registrations": sum(registrations),
        "active_users": sum(active_users),
        "posts": sum(posts),
        "comments": sum(comments),
        "likes": sum(likes),
        "messages": sum(messages),
        "notifications": sum(notifications),
        "reports": sum(reports),
        "friend_requests": sum(friend_requests_created),
        "friend_requests_accepted": sum(friend_requests_accepted),
        "monthly_active_users": sum(monthly_active),
        "engagement": sum(likes) + sum(comments),
        "stories": (
            Story.objects.count() if permissions["stories"] else 0
        ),
        "active_stories": (
            Story.objects.filter(expires_at__gt=timezone.now()).count()
            if permissions["stories"]
            else 0
        ),
        "expired_stories": (
            Story.objects.filter(expires_at__lte=timezone.now()).count()
            if permissions["stories"]
            else 0
        ),
        "story_reactions": (
            StoryReaction.objects.count()
            if permissions["story_reactions"] and story_reactions_available
            else ("—" if permissions["story_reactions"] else 0)
        ),
    }

    # Reaction distribution by type
    reactions_by_type = {}
    if permissions["story_reactions"]:
        if story_reactions_available:
            for choice in StoryReaction.ReactionType.choices:
                reactions_by_type[choice[0]] = StoryReaction.objects.filter(
                    reaction_type=choice[0]
                ).count()
        else:
            for choice in StoryReaction.ReactionType.choices:
                reactions_by_type[choice[0]] = "—"
    else:
        for choice in StoryReaction.ReactionType.choices:
            reactions_by_type[choice[0]] = 0

    return {
        "range_days": days,
        "range_label": RANGE_OPTIONS[days],
        "labels": labels,
        "totals": totals,
        "registrations": registrations,
        "registrations_cumulative": registrations_cumulative,
        "active_users": active_users,
        "posts": posts,
        "comments": comments,
        "likes": likes,
        "likes_cumulative": cumulative(likes),
        "comments_cumulative": cumulative(comments),
        "friend_requests_created": friend_requests_created,
        "friend_requests_accepted": friend_requests_accepted,
        "reports": reports,
        "messages": messages,
        "notifications": notifications,
        "monthly_active_labels": [month.strftime("%b %Y") for month in months],
        "monthly_active_users": monthly_active,
        "engagement_values": [sum(likes), sum(comments)],
        "friend_request_trend_total": sum(friend_requests_created)
        + sum(friend_requests_accepted),
        "popular_posts": popular_posts,
        "top_users": top_users,
        "reactions_by_type": reactions_by_type,
        "permissions": permissions,
        "has_activity_data": any(
            [
                sum(registrations),
                sum(active_users),
                sum(posts),
                sum(comments),
                sum(likes),
                sum(messages),
                sum(notifications),
                sum(reports),
                sum(friend_requests_created),
                sum(friend_requests_accepted),
                sum(monthly_active),
            ]
        ),
    }

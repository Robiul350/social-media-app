
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db import transaction

from social.access import is_blocked_between

from .models import Notification, NotificationPreference


def notification_group_name(user_id):
    return f"notifications_{user_id}"


def create_notification(
    recipient,
    sender,
    notification_type,
    post=None,
    comment=None
):
    if recipient == sender or is_blocked_between(recipient, sender):
        return

    preference, _ = NotificationPreference.objects.get_or_create(user=recipient)
    preference_map = {
        "like": "likes",
        "comment": "comments",
        "reply": "replies",
        "follow": "follows",
        "friend_request": "friend_requests",
        "message": "messages",
        "mention": "mentions",
        "story_reaction": "story_reactions",
    }
    preference_field = preference_map.get(notification_type)
    if preference_field and not getattr(preference, preference_field):
        return None

    notification = Notification.objects.create(
        recipient=recipient,
        sender=sender,
        notification_type=notification_type,
        post=post,
        comment=comment
    )
    channel_layer = get_channel_layer()
    if channel_layer:
        payload = {
            "id": notification.id,
            "sender": sender.id,
            "sender_username": sender.username,
            "notification_type": notification.notification_type,
            "post": post.id if post else None,
            "comment": comment.id if comment else None,
            "is_read": notification.is_read,
            "created_at": notification.created_at.isoformat(),
        }

        def publish_notification():
            async_to_sync(channel_layer.group_send)(
                notification_group_name(recipient.id),
                {
                    "type": "notification.created",
                    "notification": payload,
                },
            )

        transaction.on_commit(publish_notification)
    return notification

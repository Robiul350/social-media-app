from asgiref.sync import async_to_sync
from channels.testing import WebsocketCommunicator
from django.contrib.auth import get_user_model
from django.test import TransactionTestCase
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import AccessToken

from config.asgi import application
from posts.models import Post
from social.models import Block, Comment

from .models import Notification


User = get_user_model()


class NotificationApiTests(APITestCase):
    def setUp(self):
        self.recipient = User.objects.create_user(
            username="notification-recipient",
            email="notification-recipient@example.com",
            password="test-password",
        )
        self.other_user = User.objects.create_user(
            username="notification-other",
            email="notification-other@example.com",
            password="test-password",
        )
        self.sender = User.objects.create_user(
            username="notification-sender",
            email="notification-sender@example.com",
            password="test-password",
        )

    def test_notification_list_and_mark_read_are_scoped_to_recipient(self):
        own_notification = Notification.objects.create(
            recipient=self.recipient,
            sender=self.sender,
            notification_type="follow",
        )
        other_notification = Notification.objects.create(
            recipient=self.other_user,
            sender=self.sender,
            notification_type="follow",
        )
        self.client.force_authenticate(self.recipient)

        response = self.client.get("/api/notifications/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [item["id"] for item in response.data],
            [own_notification.id],
        )

        forbidden_read = self.client.patch(
            f"/api/notifications/{other_notification.id}/read/",
        )
        self.assertEqual(forbidden_read.status_code, 404)

        own_read = self.client.patch(
            f"/api/notifications/{own_notification.id}/read/",
        )
        self.assertEqual(own_read.status_code, 200)
        own_notification.refresh_from_db()
        other_notification.refresh_from_db()
        self.assertTrue(own_notification.is_read)
        self.assertFalse(other_notification.is_read)

    def test_notification_hides_post_reference_after_block(self):
        post = Post.objects.create(author=self.sender, content="Public post")
        notification = Notification.objects.create(
            recipient=self.recipient,
            sender=self.sender,
            notification_type="like",
            post=post,
        )
        Block.objects.create(blocker=self.sender, blocked=self.recipient)
        self.client.force_authenticate(self.recipient)

        response = self.client.get("/api/notifications/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]["id"], notification.id)
        self.assertIsNone(response.data[0]["post"])

    def test_reply_notifies_parent_comment_author(self):
        post = Post.objects.create(author=self.recipient, content="A post")
        parent = Comment.objects.create(
            post=post,
            user=self.other_user,
            content="A top-level comment",
        )
        self.client.force_authenticate(self.sender)

        response = self.client.post(
            f"/api/social/posts/{post.id}/comments/",
            {"content": "A reply", "parent": parent.id},
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(
            Notification.objects.filter(
                recipient=self.other_user,
                sender=self.sender,
                notification_type="reply",
                comment_id=response.data["id"],
                post=post,
            ).exists()
        )
        self.assertFalse(
            Notification.objects.filter(
                recipient=self.recipient,
                sender=self.sender,
                notification_type="reply",
            ).exists()
        )


class NotificationWebsocketTests(TransactionTestCase):
    def setUp(self):
        self.recipient = User.objects.create_user(
            username="socket-notification-recipient",
            email="socket-notification-recipient@example.com",
            password="test-password",
        )
        self.sender = User.objects.create_user(
            username="socket-notification-sender",
            email="socket-notification-sender@example.com",
            password="test-password",
        )

    def test_jwt_user_receives_new_notification(self):
        token = AccessToken.for_user(self.recipient)

        async def receive_notification():
            communicator = WebsocketCommunicator(
                application,
                f"/ws/notifications/?token={token}",
            )
            connected, _ = await communicator.connect()
            self.assertTrue(connected)

            from channels.db import database_sync_to_async
            from notifications.utils import create_notification

            await database_sync_to_async(create_notification)(
                recipient=self.recipient,
                sender=self.sender,
                notification_type="follow",
            )
            message = await communicator.receive_json_from()
            self.assertEqual(message["type"], "notification")
            self.assertEqual(message["notification"]["sender"], self.sender.id)
            self.assertEqual(
                message["notification"]["notification_type"],
                "follow",
            )
            await communicator.disconnect()

        async_to_sync(receive_notification)()

    def test_websocket_rejects_missing_jwt(self):
        async def reject_connection():
            communicator = WebsocketCommunicator(
                application,
                "/ws/notifications/",
            )
            connected, close_code = await communicator.connect()
            self.assertFalse(connected)
            self.assertEqual(close_code, 4401)

        async_to_sync(reject_connection)()

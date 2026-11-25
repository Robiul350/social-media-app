import json

from asgiref.sync import async_to_sync
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TransactionTestCase
from django.utils import timezone
from channels.testing import HttpCommunicator, WebsocketCommunicator
from config.asgi import application
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import AccessToken

from notifications.models import Notification

from social.models import Block

from .models import Message


User = get_user_model()


class ConversationTests(APITestCase):
    def setUp(self):
        self.sender = User.objects.create_user(
            username="chat-sender",
            email="chat-sender@example.com",
            password="test-password",
        )
        self.recipient = User.objects.create_user(
            username="chat-recipient",
            email="chat-recipient@example.com",
            password="test-password",
        )
        self.client.force_authenticate(self.sender)

    def test_rest_message_creates_notification_for_recipient(self):
        response = self.client.post(
            f"/api/chat/conversations/{self.recipient.id}/",
            {"content": "Hello"},
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Message.objects.count(), 1)
        self.assertTrue(
            Notification.objects.filter(
                recipient=self.recipient,
                sender=self.sender,
                notification_type="message",
            ).exists()
        )

    def test_chat_attachment_rejects_unsupported_file_types(self):
        upload = SimpleUploadedFile(
            "malware.exe",
            b"MZ\x00\x00",
            content_type="application/octet-stream",
        )
        response = self.client.post(
            f"/api/chat/conversations/{self.recipient.id}/",
            {"content": "See attachment", "attachment": upload},
            format="multipart",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("attachment", response.data)
        self.assertEqual(Message.objects.count(), 0)

    def test_blocked_user_cannot_read_or_list_the_blocked_conversation(self):
        Block.objects.create(blocker=self.recipient, blocked=self.sender)
        Message.objects.create(
            sender=self.recipient,
            receiver=self.sender,
            content="Hidden message",
        )

        self.assertEqual(
            self.client.post(f"/api/chat/conversations/{self.recipient.id}/read/").status_code,
            404,
        )
        self.assertEqual(self.client.get("/api/chat/conversations/").data, [])
        self.assertEqual(
            self.client.get("/api/chat/unread-count/").data["unread_count"],
            0,
        )

    def test_soft_deleted_messages_are_excluded_from_history_and_unread_counts(self):
        message = Message.objects.create(
            sender=self.recipient,
            receiver=self.sender,
            content="Deleted message",
        )
        message.deleted_at = timezone.now()
        message.save(update_fields=["deleted_at"])

        self.assertEqual(
            self.client.get(f"/api/chat/conversations/{self.recipient.id}/").data,
            [],
        )
        self.assertEqual(
            self.client.get("/api/chat/unread-count/").data["unread_count"],
            0,
        )

    def test_group_creation_rejects_unknown_and_blocked_members(self):
        stranger = User.objects.create_user(
            username="group-stranger",
            email="group-stranger@example.com",
            password="test-password",
        )
        blocked = User.objects.create_user(
            username="group-blocked",
            email="group-blocked@example.com",
            password="test-password",
        )
        Block.objects.create(blocker=self.sender, blocked=blocked)

        invalid = self.client.post(
            "/api/chat/groups/",
            {"name": "Team", "member_ids": [999999]},
            format="json",
        )
        self.assertEqual(invalid.status_code, 400)

        blocked_response = self.client.post(
            "/api/chat/groups/",
            {"name": "Team", "member_ids": [blocked.id]},
            format="json",
        )
        self.assertEqual(blocked_response.status_code, 400)

        valid = self.client.post(
            "/api/chat/groups/",
            {"name": "Team", "member_ids": [stranger.id]},
            format="json",
        )
        self.assertEqual(valid.status_code, 201)

    def test_group_messages_do_not_break_direct_conversation_list(self):
        member = User.objects.create_user(
            username="group-list-member",
            email="group-list-member@example.com",
            password="test-password",
        )
        group = self.client.post(
            "/api/chat/groups/",
            {"name": "Team", "member_ids": [member.id]},
            format="json",
        ).data
        created = self.client.post(
            f"/api/chat/groups/{group['id']}/messages/",
            {"content": "Group update"},
            format="json",
        )
        self.assertEqual(created.status_code, 201)

        response = self.client.get("/api/chat/conversations/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])

    def test_group_messages_from_blocked_members_are_hidden(self):
        member = User.objects.create_user(
            username="group-member",
            email="group-member@example.com",
            password="test-password",
        )
        group = self.client.post(
            "/api/chat/groups/",
            {"name": "Team", "member_ids": [member.id]},
            format="json",
        ).data
        self.client.force_authenticate(user=member)
        self.client.post(
            f"/api/chat/groups/{group['id']}/messages/",
            {"content": "Visible before block"},
            format="json",
        )

        Block.objects.create(blocker=self.sender, blocked=member)
        self.client.force_authenticate(user=self.sender)
        messages = self.client.get(f"/api/chat/groups/{group['id']}/messages/")

        self.assertEqual(messages.status_code, 200)
        self.assertEqual(messages.data, [])


class ChatWebsocketTests(TransactionTestCase):
    def setUp(self):
        self.sender = User.objects.create_user(
            username="socket-sender",
            email="socket-sender@example.com",
            password="test-password",
        )
        self.recipient = User.objects.create_user(
            username="socket-recipient",
            email="socket-recipient@example.com",
            password="test-password",
        )

    def test_jwt_authenticated_users_exchange_messages_typing_and_presence(self):
        sender_token = AccessToken.for_user(self.sender)
        recipient_token = AccessToken.for_user(self.recipient)

        async def interact():
            sender_socket = WebsocketCommunicator(
                application,
                f"/ws/chat/{self.recipient.id}/?token={sender_token}",
            )
            connected, _ = await sender_socket.connect()
            self.assertTrue(connected)
            self.assertEqual(
                (await sender_socket.receive_json_from())["type"],
                "presence",
            )

            recipient_socket = WebsocketCommunicator(
                application,
                f"/ws/chat/{self.sender.id}/?token={recipient_token}",
            )
            connected, _ = await recipient_socket.connect()
            self.assertTrue(connected)
            self.assertEqual(
                (await recipient_socket.receive_json_from())["type"],
                "presence",
            )
            sender_presence = await sender_socket.receive_json_from()
            self.assertEqual(sender_presence["user_id"], self.recipient.id)
            self.assertTrue(sender_presence["is_online"])

            await sender_socket.send_json_to({
                "type": "typing",
                "is_typing": True,
            })
            sender_typing = await sender_socket.receive_json_from()
            recipient_typing = await recipient_socket.receive_json_from()
            self.assertEqual(sender_typing["type"], "typing")
            self.assertEqual(recipient_typing["type"], "typing")
            self.assertTrue(recipient_typing["is_typing"])

            await sender_socket.send_json_to({"message": "Live message"})
            sent_message = await sender_socket.receive_json_from()
            received_message = await recipient_socket.receive_json_from()
            self.assertEqual(sent_message["id"], received_message["id"])
            self.assertEqual(received_message["message"], "Live message")

            await sender_socket.disconnect()
            offline_presence = await recipient_socket.receive_json_from()
            self.assertFalse(offline_presence["is_online"])
            await recipient_socket.disconnect()

        async_to_sync(interact)()

    def test_websocket_rejects_missing_or_invalid_jwt(self):
        async def reject_connections():
            for url in (
                f"/ws/chat/{self.recipient.id}/",
                f"/ws/chat/{self.recipient.id}/?token=invalid",
            ):
                communicator = WebsocketCommunicator(application, url)
                connected, close_code = await communicator.connect()
                self.assertFalse(connected)
                self.assertEqual(close_code, 4401)

        async_to_sync(reject_connections)()

    def test_websocket_rejects_inactive_user(self):
        token = AccessToken.for_user(self.sender)
        self.sender.is_active = False
        self.sender.save(update_fields=["is_active"])

        async def reject_connection():
            communicator = WebsocketCommunicator(
                application,
                f"/ws/chat/{self.recipient.id}/?token={token}",
            )
            connected, close_code = await communicator.connect()
            self.assertFalse(connected)
            self.assertEqual(close_code, 4401)

        async_to_sync(reject_connection)()

    def test_websocket_rejects_blocked_conversation(self):
        Block.objects.create(blocker=self.sender, blocked=self.recipient)
        token = AccessToken.for_user(self.sender)

        async def reject_connection():
            communicator = WebsocketCommunicator(
                application,
                f"/ws/chat/{self.recipient.id}/?token={token}",
            )
            connected, close_code = await communicator.connect()
            self.assertFalse(connected)
            self.assertEqual(close_code, 4403)

        async_to_sync(reject_connection)()

    def test_marking_messages_read_broadcasts_a_receipt(self):
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.recipient,
            content="Read receipt test",
        )
        recipient_token = AccessToken.for_user(self.recipient)

        async def interact():
            socket = WebsocketCommunicator(
                application,
                f"/ws/chat/{self.sender.id}/?token={recipient_token}",
            )
            connected, _ = await socket.connect()
            self.assertTrue(connected)
            await socket.receive_json_from()

            request = HttpCommunicator(
                application,
                "POST",
                f"/api/chat/conversations/{self.sender.id}/read/",
                body=b"{}",
                headers=[
                    (b"authorization", f"Bearer {recipient_token}".encode()),
                    (b"content-type", b"application/json"),
                    (b"host", b"localhost"),
                ],
            )
            response = await request.get_response()
            self.assertEqual(
                response["status"],
                200,
                response["body"].decode(),
            )
            receipt = await socket.receive_json_from()
            self.assertEqual(receipt["type"], "read_receipt")
            self.assertEqual(receipt["reader_id"], self.recipient.id)
            self.assertEqual(receipt["message_ids"], [message.id])
            await socket.disconnect()

        async_to_sync(interact)()
        message.refresh_from_db()
        self.assertTrue(message.is_read)

    def test_rest_message_is_delivered_to_an_active_websocket(self):
        sender_token = AccessToken.for_user(self.sender)
        recipient_token = AccessToken.for_user(self.recipient)

        async def interact():
            socket = WebsocketCommunicator(
                application,
                f"/ws/chat/{self.sender.id}/?token={recipient_token}",
            )
            connected, _ = await socket.connect()
            self.assertTrue(connected)
            await socket.receive_json_from()

            body = json.dumps({"content": "REST delivery"}).encode()
            request = HttpCommunicator(
                application,
                "POST",
                f"/api/chat/conversations/{self.recipient.id}/",
                body=body,
                headers=[
                    (b"authorization", f"Bearer {sender_token}".encode()),
                    (b"content-type", b"application/json"),
                    (b"content-length", str(len(body)).encode()),
                    (b"host", b"localhost"),
                ],
            )
            response = await request.get_response()
            self.assertEqual(response["status"], 201, response["body"].decode())
            message = await socket.receive_json_from()
            self.assertEqual(message["message"], "REST delivery")
            await socket.disconnect()

        async_to_sync(interact)()

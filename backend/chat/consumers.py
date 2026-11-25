
import json

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model

from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError

from .models import Message
from .utils import conversation_group_name
from notifications.utils import create_notification
from social.access import can_chat_between

User = get_user_model()


class ChatConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        self.user = self.scope["user"]

        if not self.user or not self.user.is_authenticated:
            await self.close(code=4401)
            return

        self.other_user_id = self.scope["url_route"]["kwargs"]["user_id"]

        if self.other_user_id == self.user.id:
            await self.close(code=4400)
            return

        self.room_group_name = conversation_group_name(
            self.user.id,
            self.other_user_id,
        )

        other_user = await self.get_other_user(self.other_user_id)

        if not other_user:
            await self.close(code=4404)
            return
        if not await self.can_chat(other_user):
            await self.close(code=4403)
            return

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "presence_update",
                "user_id": self.user.id,
                "is_online": True,
            },
        )

    async def disconnect(self, close_code):
        if hasattr(self, "room_group_name"):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "presence_update",
                    "user_id": self.user.id,
                    "is_online": False,
                },
            )

    async def receive_json(self, content, **kwargs):
        # Permissions can change while a socket is open (block, deactivation,
        # privacy setting). Re-check on every message, not just at connect.
        if not await self.can_still_chat():
            await self.close(code=4403)
            return

        if content.get("type") == "typing":
            is_typing = content.get("is_typing")
            if isinstance(is_typing, bool):
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "typing_update",
                        "user_id": self.user.id,
                        "is_typing": is_typing,
                    },
                )
            return

        raw_message = content.get("message", "")
        if not isinstance(raw_message, str):
            await self.send_json({
                "error": "Message must be text."
            })
            return
        text = raw_message.strip()

        if not text:
            await self.send_json({
                "error": "Message cannot be empty."
            })
            return

        if len(text) > 5000:
            await self.send_json({
                "error": "Message is too long."
            })
            return

        message = await self.save_message(
            self.user.id,
            self.other_user_id,
            text
        )
        message["sender_username"] = self.user.username
        await self.create_message_notification(
            self.user.id,
            self.other_user_id
        )

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message["content"],
                "sender_id": message["sender_id"],
                "sender_username": message["sender_username"],
                "receiver_id": message["receiver_id"],
                "id": message["id"],
                "created_at": message["created_at"],
                "is_read": False,
            }
        )

    async def chat_message(self, event):
        await self.send_json(event)

    async def typing_update(self, event):
        await self.send_json({
            "type": "typing",
            "user_id": event["user_id"],
            "is_typing": event["is_typing"],
        })

    async def presence_update(self, event):
        await self.send_json({
            "type": "presence",
            "user_id": event["user_id"],
            "is_online": event["is_online"],
        })

    async def read_receipt(self, event):
        await self.send_json({
            "type": "read_receipt",
            "reader_id": event["reader_id"],
            "message_ids": event["message_ids"],
        })

    async def message_updated(self, event):
        await self.send_json(event)

    async def message_deleted(self, event):
        await self.send_json(event)

    @database_sync_to_async
    def get_other_user(self, user_id):
        return User.objects.select_related("profile").filter(id=user_id).first()

    @database_sync_to_async
    def can_chat(self, other_user):
        return can_chat_between(self.user, other_user)

    @database_sync_to_async
    def can_still_chat(self):
        current_user = User.objects.filter(id=self.user.id, is_active=True).first()
        other_user = User.objects.select_related("profile").filter(id=self.other_user_id).first()
        if not current_user or not other_user:
            return False
        return can_chat_between(current_user, other_user)

    @database_sync_to_async
    def save_message(self, sender_id, receiver_id, text):
        message = Message.objects.create(
            sender_id=sender_id,
            receiver_id=receiver_id,
            content=text
        )

        return {
            "id": message.id,
            "sender_id": message.sender_id,
            "receiver_id": message.receiver_id,
            "content": message.content,
            "created_at": message.created_at.isoformat(),
            "is_read": message.is_read,
        }

    @database_sync_to_async
    def create_message_notification(self, sender_id, receiver_id):
        sender = User.objects.get(id=sender_id)
        recipient = User.objects.get(id=receiver_id)
        create_notification(
            recipient=recipient,
            sender=sender,
            notification_type="message",
        )

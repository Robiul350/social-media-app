from channels.generic.websocket import AsyncJsonWebsocketConsumer

from .utils import notification_group_name


class NotificationConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        user = self.scope.get("user")
        if not user or not user.is_authenticated:
            await self.close(code=4401)
            return

        self.group_name = notification_group_name(user.id)
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, _close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive_json(self, content, **kwargs):
        # The notifications socket only pushes events. Ignore client pings so
        # Channels does not fall through to its NotImplementedError handler.
        return None

    async def notification_created(self, event):
        await self.send_json({
            "type": "notification",
            "notification": event["notification"],
        })

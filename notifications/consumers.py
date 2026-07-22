import json
from collections import defaultdict
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils import timezone
from datetime import timedelta


class NotificationConsumer(AsyncWebsocketConsumer):
    RATE_LIMIT = 30  # max messages per minute
    _rate_tracker = defaultdict(list)

    async def connect(self):
        self.user = self.scope["user"]
        if not self.user.is_authenticated:
            await self.close()
            return
        self.group_name = f"user_{self.user.id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def send_notification(self, event):
        now = timezone.now()
        window_start = now - timedelta(minutes=1)
        user_key = str(self.user.id)
        self._rate_tracker[user_key] = [
            t for t in self._rate_tracker[user_key] if t > window_start
        ]
        if len(self._rate_tracker[user_key]) >= self.RATE_LIMIT:
            await self.send(text_data=json.dumps({
                "type": "error",
                "message": "Rate limit exceeded",
            }))
            return
        self._rate_tracker[user_key].append(now)
        await self.send(text_data=json.dumps(event["data"]))

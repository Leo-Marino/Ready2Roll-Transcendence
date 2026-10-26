import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import DirectMessage

User = get_user_model()

class DMConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if self.user.is_anonymous:
            await self.close()
            return

        self.other_user_id = int(self.scope['url_route']['kwargs']['user_id'])

        # Sort IDs so User 1 -> User 5 and User 5 -> User 1 join the same room: "dm_1_5"
        low_id, high_id = sorted([self.user.id, self.other_user_id])
        self.room_group_name = f"dm_{low_id}_{high_id}"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        text = data.get("text", "").strip()
        if not text:
            return

        # 1. Save message to PostgreSQL
        msg = await self.save_message(self.user.id, self.other_user_id, text)

        # 2. Broadcast message to the Redis room
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "id": msg.id,
                "sender_id": self.user.id,
                "sender": self.user.username,
                "text": msg.content,
                "created_at": msg.created_at.isoformat(),
            }
        )

    async def chat_message(self, event):
        # Send the broadcasted message down the WebSocket to Vue
        await self.send(text_data=json.dumps({
            "id": event["id"],
            "sender_id": event["sender_id"],
            "sender": event["sender"],
            "text": event["text"],
            "isMe": event["sender_id"] == self.user.id,
            "created_at": event["created_at"],
        }))

    @database_sync_to_async
    def save_message(self, sender_id, receiver_id, text):
        return DirectMessage.objects.create(
            sender_id=sender_id,
            receiver_id=receiver_id,
            content=text
        )

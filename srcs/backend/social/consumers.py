import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import DirectMessage
from .realtime import GLOBAL_GROUP, user_group, set_user_online, set_user_offline

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

        # 3. Tell the receiver (on any page) that a new message arrived -> dot on the chat icon
        await self.channel_layer.group_send(
            user_group(self.other_user_id),
            {"type": "message_push", "target_id": self.other_user_id},
        )

    async def chat_message(self, event):
        # This socket is open on this conversation, so a message coming from the
        # other user is seen right away -> mark it as read (no dot in the sidebar).
        if event["sender_id"] != self.user.id:
            await self.mark_read(event["id"])
            # The receiver was already pinged on send: ping again so the dot goes away
            await self.channel_layer.group_send(
                user_group(self.user.id),
                {"type": "message_push", "target_id": self.user.id},
            )

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

    @database_sync_to_async
    def mark_read(self, message_id):
        DirectMessage.objects.filter(pk=message_id, is_read=False).update(is_read=True)

class SocialConsumer(AsyncWebsocketConsumer):
    """One connection per browser tab. It receives live updates only
    (likes, comments, reactions, follows, notification signals); it never
    expects messages from the client."""

    async def connect(self):
        self.user = self.scope["user"]
        if self.user.is_anonymous:
            await self.close()
            return

        self.group_names = [GLOBAL_GROUP, user_group(self.user.id)]
        for group in self.group_names:
            await self.channel_layer.group_add(group, self.channel_name)
        await self.accept()
        await database_sync_to_async(set_user_online)(self.user.id)

    async def disconnect(self, close_code):
        if hasattr(self, "user") and not self.user.is_anonymous:
            await database_sync_to_async(set_user_offline)(self.user.id)
        for group in getattr(self, "group_names", []):
            await self.channel_layer.group_discard(group, self.channel_name)

    # Called by group_send(..., {"type": "social_action", ...})
    async def social_action(self, event):
        await self.send(text_data=json.dumps({
            "action": event["action"],
            "target_id": event["target_id"],
            "data": event.get("data", {}),
        }))

    # Called by group_send(..., {"type": "notification_push", ...})
    async def notification_push(self, event):
        await self.send(text_data=json.dumps({
            "action": "notification",
            "target_id": event["target_id"],
            "data": {},
        }))

    # Called by group_send(..., {"type": "message_push", ...})
    async def message_push(self, event):
        await self.send(text_data=json.dumps({
            "action": "message",
            "target_id": event["target_id"],
            "data": {},
        }))

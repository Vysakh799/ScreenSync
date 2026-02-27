# app/consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from app.models import Session


class SessionConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.user = self.scope["user"]

        # 🔐 Check authentication
        if not self.user.is_authenticated:
            await self.close()
            return

        self.admin_id = self.scope["url_route"]["kwargs"]["admin_id"]

        # 🔐 Ensure user can only join their own admin room
        if str(self.user.id) != self.admin_id:
            await self.close()
            return

        self.room_group_name = f"admin_{self.admin_id}"

        print("CONNECTED:", self.room_group_name)

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        print("DISCONNECTED:", self.room_group_name)

        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        print("RECEIVED:", text_data)

        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            return

        session_id = data.get("session_id")

        student_name = None

        if session_id:
            student_name = await self.get_student_name(session_id)

        # Attach student name before forwarding
        data["student_name"] = student_name

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "forward_message",
                "message": data,
            }
        )

    async def forward_message(self, event):
        await self.send(
            text_data=json.dumps(event["message"])
        )

    async def session_ended(self, event):
        await self.send(
            text_data=json.dumps({
                "type": "session_ended",
                "session_id": event["session_id"],
                
            })
        )


    @database_sync_to_async
    def get_student_name(self, session_id):
        try:
            session = Session.objects.get(id=session_id)
            return session.student_name
        except Session.DoesNotExist:
            return "Unknown Student"
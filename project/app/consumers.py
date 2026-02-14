import json
from channels.generic.websocket import AsyncWebsocketConsumer


class SessionConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.admin_id = self.scope['url_route']['kwargs']['admin_id']
        self.room_group_name = f"admin_{self.admin_id}"

        print("CONNECT:", self.room_group_name)

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        print("RECEIVED:", text_data)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "forward_message",
                "message": text_data
            }
        )

    async def forward_message(self, event):
        await self.send(text_data=event["message"])

    async def session_ended(self, event):
        await self.send(text_data=json.dumps({
            "type": "session_ended",
            "session_id": event["session_id"]
        }))


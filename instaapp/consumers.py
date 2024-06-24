import json
from channels.generic.websocket import AsyncWebsocketConsumer
from instaapp.models.chatroom import ChatRoom, Message
from instaapp.models.user import CustomUser
from instaapp.serializers import MessageSerializer
from channels.db import database_sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chatroom_id = self.scope['url_route']['kwargs']['chatroom_id']
        self.chatroom_group_name = f'chat_{self.chatroom_id}'

        # Join room group
        await self.channel_layer.group_add(
            self.chatroom_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.chatroom_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        sender_id = data['sender_id']
        receiver_id = data['receiver_id']

        sender = await self.get_user(sender_id)
        receiver = await self.get_user(receiver_id)
        chatroom = await self.get_chatroom(self.chatroom_id)

        message_instance = await self.create_message(chatroom, sender, receiver, message)
        serialized_message = MessageSerializer(message_instance).data

        await self.channel_layer.group_send(
            self.chatroom_group_name,
            {
                'type': 'chat_message',
                'message': serialized_message
            }
        )

    async def chat_message(self, event):
        message = event['message']

        await self.send(text_data=json.dumps({
            'message': message
        }))

    @database_sync_to_async
    def get_user(self, user_id):
        return CustomUser.objects.get(id=user_id)

    @database_sync_to_async
    def get_chatroom(self, chatroom_id):
        return ChatRoom.objects.get(id=chatroom_id)

    @database_sync_to_async
    def create_message(self, chatroom, sender, receiver, content):
        return Message.objects.create(chatroom=chatroom, sender=sender, receiver=receiver, content=content)
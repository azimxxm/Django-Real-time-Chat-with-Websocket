# chat/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from chat.models import Post
import asyncio


from chat.serializer import PostSerializer
from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        print("channel name => ", self.channel_name)
        print("room_group name => ", self.room_group_name)  # chat_room1

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    # hammadan qabul qilish
    async def receive(self, text_data):
        print('Receive message from WebSocket')
        print("user => ", self.scope['user'].username)
        print("receive function text_data" + text_data)
        print("scope =>", self.scope)
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'message',
                'message': message,
                'name': self.scope['user'].username
            }
        )

    # Receive message from room group
    async def message(self, event):
        print('Receive message from room group')
        print("event => ", event)
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'name': event['name'],
            "type": event['type']
        }))

@sync_to_async
def get_all_posts():
    posts = Post.objects.all()
    serializer = PostSerializer(posts, many=True)
    return serializer.data

class PostConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'post'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        
        # await all post from database
        posts = await get_all_posts()
        for post in posts:
            await self.send(text_data=json.dumps({
                'message': post
            }))

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        post_data_json = json.loads(text_data)

        serializer = PostSerializer(data={
            'title': post_data_json['message']['title'],
            'content': post_data_json['message']['content']
        })
        # save post to database use a thread or sync_to_async
        if serializer.is_valid():
            await database_sync_to_async(serializer.save)()

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'post',
                    'message': serializer.data
                }
            )
        else:
            await self.send(text_data=json.dumps({
                'message': serializer.errors,
                'type': 'error'
            }))

    # Receive message from room group
    async def post(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))
        
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
import json


class GameRoom(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'room_%s' % self.room_name

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

        username = await self.remove_user()
        if username:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'system_message',
                    'message': f'User {username} left the room.',
                }
            )

    @database_sync_to_async
    def remove_user(self):
        user = self.scope.get("user")
        if user and user.is_authenticated:
            username = user.username
            user.delete()
            return username
        return None

    async def system_message(self, event):
        await self.send(text_data=json.dumps({
            'type': event['type'],
            'message': event['message'],
        }))

    async def receive(self, text_data=None, bytes_data=None):
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type', '')
            print(f"Received message of type: {message_type}")
            if message_type == 'player-ready':
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'player_ready',
                        'player_num': text_data_json.get('player_num', 0)
                    }
                )
            elif message_type == 'fire':
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'fire',
                        'shot_fired': text_data_json.get('shot_fired', -1)
                    }
                )
            elif message_type == 'fire-reply':
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'fire_reply',
                        'class_list': text_data_json.get('class_list', [])
                    }
                )
            elif message_type == 'enemy-ready':
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'enemy_ready',
                        'player_num': text_data_json.get('player_num', 0)
                    }
                )
            elif message_type == 'chat_message':
                message = text_data_json['message']
                username = text_data_json['username']

                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'message': message,
                        'username': username,
                    })

        except KeyError as e:
            print(f"Invalid message format: Missing key {e}")
            return
        except json.JSONDecodeError as e:
            print(f"Invalid message format: {e}")
            return

    async def chat_message(self, event):
        message = event['message']
        username = event['username']
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': message,
            'username': username,
        }))

    async def player_ready(self, event):
        player_num = event['player_num']
        print(f"Player {player_num} is ready")
        await self.send(text_data=json.dumps({
            'type': 'player_ready',
            'player_num': player_num
        }))

    async def fire(self, event):
        shot_fired = event['shot_fired']
        await self.send(text_data=json.dumps({
            'type': 'fire',
            'shot_fired': shot_fired
        }))

    async def fire_reply(self, event):
        class_list = event['class_list']
        await self.send(text_data=json.dumps({
            'type': 'fire_reply',
            'class_list': class_list
        }))

    async def enemy_ready(self, event):
        player_num = event['player_num']
        await self.send(text_data=json.dumps({
            'type': 'enemy_ready',
            'player_num': player_num
        }))
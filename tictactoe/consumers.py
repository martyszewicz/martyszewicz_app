from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
import json
from .models import TictactoeRoom
from django.utils.translation import gettext as _


class GameRoom(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'room_%s' % self.room_name

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'update_players',
                'players': await self.get_players(),
            }
        )

        user = self.scope.get("user")
        if user and user.is_authenticated:
            username = user.username

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'system_message',
                    'message': _('Użytkownik {username} dołączył do pokoju.').format(username=username),
                }
            )

        await self.accept()

    async def disconnect(self, close_code):
        username = await self.remove_user()
        if username:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'system_message',
                    'message': _('Użytkownik {username} opuścił.').format(username=username)
                }
            )
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    @database_sync_to_async
    def get_players(self):
        room = TictactoeRoom.objects.get(room_name=self.room_name)
        return {
            'player1': room.game_creator.username,
            'player2': room.game_opponent.username if room.game_opponent else None,
        }

    @database_sync_to_async
    def remove_user(self):
        user = self.scope.get("user")
        if user and user.is_authenticated:
            username = user.username
            user.delete()
            return username
        return None

    async def update_players(self, event):
        players = await self.get_players()
        game_creator = players['player1']
        opponent = players['player2']

        await self.send(text_data=json.dumps({
            'type': 'update_players',
            'game_creator': game_creator,
            'opponent': opponent,
        }))

    async def game_end (self, event):
        await self.send(text_data=json.dumps({
            'type': event["type"],
            'player': event["player"]
        }))

    async def system_message(self, event):
        await self.send(text_data=json.dumps({
            'type': event['type'],
            'message': event['message'],
        }))

    async def receive(self, text_data=None, bytes_data=None):
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type', '')

            if message_type == 'game_end':
                player = text_data_json['player']

                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'game_end',
                        'player': player,
                    })

            if message_type == 'chat_message':
                message = text_data_json['message']
                username = text_data_json['username']

                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'message': message,
                        'username': username,
                    })

            if message_type == "players_choice":
                player = text_data_json['player']
                index = text_data_json['index']
                value = text_data_json['value']

                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'players_choice',
                        'player': player,
                        'index': index,
                        'value': value,
                    }
                )

        except KeyError as e:
            print(f"Invalid message format: Missing key {e}")
            return
        except json.JSONDecodeError as e:
            print(f"Invalid message format: {e}")
            return

    async def players_choice(self, event):
        player = event['player']
        index = event['index']
        value = event['value']
        await self.send(text_data=json.dumps({
            'type': 'players_choice',
            'player': player,
            'index': index,
            'value': value,
        }))

    async def chat_message(self, event):
        message = event['message']
        username = event['username']
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': message,
            'username': username,
        }))


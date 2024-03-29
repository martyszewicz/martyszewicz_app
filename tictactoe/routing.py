from .consumers import GameRoom
from django.urls import re_path

websocket_urlpatterns = [
    re_path(r'/ws/tictactoe/multi_player/(?P<room_name>\w+)', GameRoom.as_asgi()),
]

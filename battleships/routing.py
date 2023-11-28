from .consumers import GameRoom
from django.urls import path

websocket_urlpatterns=[
    path('ws/play/<room_name>/',GameRoom.as_asgi(),name="clicked"),
]
from django.urls import re_path
from tic_tac_toe.consumers.websocket import TicTacToeConsumer

websocket_urlpatterns = [
    re_path(r'ws/tic_tac_toe/$', TicTacToeConsumer.as_asgi()),
]
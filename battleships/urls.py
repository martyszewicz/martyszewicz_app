from django.urls import path
from .views import *


urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('new_game', NewGameView.as_view(), name='new_game'),
    path('join_game', JoinGameView.as_view(), name='join_game'),
    path('play/<room_code>', PlayView.as_view(), name='play'),
]
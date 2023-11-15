from django.urls import path
from .views import *

ulrpatterns = [
    path('', home, name='home'),
    path('new_game', new_game, name='new_game'),
    path('join_game', join_game, name='join_game'),
    path('play/<room_code>', play, name='play'),
]
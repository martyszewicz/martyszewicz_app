from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('new_game', NewGameView.as_view(), name='new_game'),
    path('join_game', JoinGameView.as_view(), name='join_game'),
    path('multi_player/<room_name>', Multi_player.as_view(), name='multi_player'),
    path('change_language/<str:language_code>/', ChangeLanguageView.as_view(), name='change_language'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
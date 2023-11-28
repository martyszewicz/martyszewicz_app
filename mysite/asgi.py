"""
ASGI config for mysite project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import battleships.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': AuthMiddlewareStack(
        URLRouter(
            battleships.routing.websocket_urlpatterns
        )
    )
})


#
# import os
# from django.urls import re_path
# from channels.routing import ProtocolTypeRouter, URLRouter
# from channels.auth import AuthMiddlewareStack
# from battleships.consumers import GameRoom
# from django.core.asgi import get_asgi_application
#
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
#
# http_application = get_asgi_application()
#
# ws_pattern = [
#     re_path(r'^battleships/ws/game/(?P<room_code>\w+)/$', GameRoom.as_asgi()),
# ]
#
# application = ProtocolTypeRouter(
#     {
#         'http': get_asgi_application(),
#         'websocket': AuthMiddlewareStack(URLRouter(ws_pattern)),
#     }
# )

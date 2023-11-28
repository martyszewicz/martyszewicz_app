from django.contrib import admin
from .models import Game


class GameAdmin(admin.ModelAdmin):
    list_display = ["room_code", "game_creator", "game_opponent", "is_private", "password", "is_over", "is_over"]

admin.site.register(Game, GameAdmin)

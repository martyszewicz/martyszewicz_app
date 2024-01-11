from django.contrib import admin
from .models import TictactoeRoom


class TictactoeRoomAdmin(admin.ModelAdmin):
    list_display = ["room_name", "game_creator", "game_opponent", "is_private", "password"]


admin.site.register(TictactoeRoom, TictactoeRoomAdmin)


from django.contrib import admin
from .models import BattleshipsRoom, TrackPlayers


class BattleshipsRoomAdmin(admin.ModelAdmin):
    list_display = ["room_name"]


class TrackPlayersAdmin(admin.ModelAdmin):
    list_display = ["username"]



admin.site.register(BattleshipsRoom, BattleshipsRoomAdmin)
admin.site.register(TrackPlayers, TrackPlayersAdmin)

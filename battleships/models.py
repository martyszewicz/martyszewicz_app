from django.db import models


class BattleshipsRoom(models.Model):
    room_name = models.CharField(max_length=50)

    def __str__(self) -> str:
        return self.room_name


class TrackPlayers(models.Model):
    username = models.CharField(max_length=50)
    room = models.ForeignKey(BattleshipsRoom, on_delete=models.CASCADE)
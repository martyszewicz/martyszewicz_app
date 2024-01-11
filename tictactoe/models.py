from django.db import models
from django.contrib.auth.models import User


class TictactoeRoom(models.Model):
    game_creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_rooms', null=True)
    game_opponent = models.ForeignKey(User, on_delete=models.CASCADE, related_name='joined_rooms', null=True, blank=True, default=None)
    room_name = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    is_private = models.BooleanField()

    def __str__(self) -> str:
        return self.room_name

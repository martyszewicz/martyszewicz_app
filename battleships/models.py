from django.db import models


class Game(models.Model):
    room_code = models.CharField(max_length=100)
    game_creator = models.CharField(max_length=100)
    game_opponent = models.CharField(max_length=100, blank=True, null=True)
    is_private = models.BooleanField(default=False)
    password = models.CharField(max_length=100, default='')
    is_over = models.BooleanField(default=False)
    STATUS_CHOICES = [
        ('waiting', 'Waiting'),
        ('ongoing', 'Ongoing'),
        ('finished', 'Finished'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='waiting')


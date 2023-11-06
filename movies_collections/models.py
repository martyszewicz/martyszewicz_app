from django.db import models
from django.contrib.auth.models import User


class FavouritesMovies(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie_id = models.CharField(max_length=200)

    def __str__(self):
        return self.movie_id
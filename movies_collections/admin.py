from django.contrib import admin
from .models import FavouritesMovies


class FavouritesMoviesAdmin(admin.ModelAdmin):
    list_display = ["user", "movie_id"]


admin.site.register(FavouritesMovies, FavouritesMoviesAdmin)


import requests
from django.contrib import messages
from movies_collections.models import FavouritesMovies
from django.utils.translation import gettext as _


class MoviesAPI:
    BASE_URL = 'https://search.imdbot.workers.dev/'

    def search_movies(self, title):
        try:
            response = requests.get(f'{self.BASE_URL}?q={title}')

            if response.status_code != requests.codes.ok:
                return None, f"Nie można połączyć z bazą danych, kod błędu: {response.status_code}"

            data = response.json()
            list_of_searched_films = data.get('description', [])
            transformed_films = []

            for film in list_of_searched_films:
                transformed_film = {
                    'IMDB_ID': film.get('#IMDB_ID'),
                    'TITLE': film.get('#TITLE'),
                    'YEAR': film.get('#YEAR'),
                    'IMG_POSTER': film.get('#IMG_POSTER')
                }
                transformed_films.append(transformed_film)

            return transformed_films, None

        except Exception as e:
            return None, f"Błąd '{e}'"


class MovieDetailsAPI:
    BASE_URL = 'https://search.imdbot.workers.dev/'

    def get_movie_details(self, movie_id):
        try:
            response = requests.get(f'{self.BASE_URL}?tt={movie_id}')

            if response.status_code != requests.codes.ok:
                return None, f"Nie można połączyć z bazą danych, kod błędu: {response.status_code}"

            movie_data = response.json()
            return movie_data, None

        except Exception as e:
            return None, f"Błąd '{e}'"

    def transform_movie_data(self, movie_data):
        return movie_data


class FavouritesService:
    def save_movie(self, user, movie_id):
        movie_id = str(movie_id)
        record = FavouritesMovies.objects.filter(user=user, movie_id=movie_id).exists()

        if record:
            return _("Ten film już jest zapisany w bibliotece 'Ulubione'")
        else:
            FavouritesMovies.objects.create(user=user, movie_id=movie_id)
            return _("Film zapisano pomyślnie w bibliotece 'Ulubione'")

    def get_favourite_movies(self, user, request):
        fav_movies = FavouritesMovies.objects.filter(user=user)
        list_of_film_id = [movie.movie_id for movie in fav_movies]
        film_collection = []

        for film_id in list_of_film_id:
            response = requests.get(f'https://search.imdbot.workers.dev/?tt={film_id}')

            if response.status_code != requests.codes.ok:
                message = _("Nie można połączyć z bazą danych, kod błędu: {error}").format(error=response.status_code)
                messages.info(request, message)
            else:
                movie = response.json()
                film_collection.append(movie)

        return film_collection

    def delete_movie(self, user, movie_id, request):
        FavouritesMovies.objects.filter(user=user, movie_id=movie_id).delete()
        messages.info(request, _(f"Film został pomyślnie usunięty z ulubionych"))
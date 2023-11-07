from django.conf import settings
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.urls import reverse
from .forms import UserRegistrationForm, UserEditForm, AdminEditForm
from .models import FavouritesMovies
from django.http import JsonResponse
import requests
from django.utils.translation import gettext as _
from django.utils.translation import activate


def index(request):
    return render(request, "movies_collections/index.html", {'user': request.user})


def change_language(request, language_code):
    if language_code in [lang[0] for lang in settings.LANGUAGES]:
        request.session['django_language'] = language_code
        activate(language_code)
    return redirect(reverse('index'))

# Users functions below _________________________________________


def login_user(request):
    if request.method == "GET":
        return render(request, 'movies_collections/login.html', {'user': request.user})
    else:
        username = request.POST['user_name']
        password = request.POST['user_pass']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.info(request, _(f"Witaj {username}!"))
            return redirect('index')
        else:
            messages.info(request, _("Błąd logowania, spróbuj ponownie"))
            return render(request, 'movies_collections/login.html', {'login_failed': True, 'user': request.user})


def logout_user(request):
    if request.user.is_authenticated:
        logout(request)
        messages.info(request, _("Wylogowałeś się poprawnie"))
        return redirect('index')
    else:
        return redirect('index')


def new_user(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.info(request, _(f"Użytkownik {form.cleaned_data['username']} został zarejestrowany"))
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.info(request, _(f'Błąd: {error}'))

    else:
        form = UserRegistrationForm()

    return render(request, 'movies_collections/new_user.html', {'form': form, 'user': request.user})


def my_profile(request):
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=request.user)
        if form.is_valid():
            current_password = form.cleaned_data['current_password']
            new_email = form.cleaned_data['new_email']
            new_password = form.cleaned_data['new_password']

            if request.user.check_password(current_password):
                if request.user.check_password(current_password):
                    if new_email:
                        request.user.email = new_email
                        request.user.save(update_fields=['email'])
                if new_password:
                    if new_password:
                        request.user.set_password(new_password)
                        update_session_auth_hash(request, request.user)
                        request.user.save(update_fields=['password'])
                messages.success(request, _("Dane użytkownika zostały zaktualizowane."))
                return redirect('my_profile')
            else:
                messages.error(request, _("Aktualne hasło jest nieprawidłowe."))
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, _(f"Błąd w polu '{field}': {error}"))
    else:
        initial_email = request.user.email
        form = UserEditForm(instance=request.user, initial={'new_email': initial_email})

    return render(request, 'movies_collections/my_profile.html', {'form': form})


# Superuser functions below ____________________________________

def users(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('index')

    user_list = User.objects.all()
    return render(request, 'movies_collections/users.html', {'users': user_list})


def user_status_change(request, action, user_name):
    user = User.objects.get(username=user_name)
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('index')
    if action == 'status_change':
        user.is_active = not user.is_active
    elif action == 'admin_change':
        user.is_superuser = not user.is_superuser
    user.save()

    return redirect('users')


def edit_user(request, user_name):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('index')
    if user_name is None:
        messages.info(request, _("Nie ma takiego użytkownika"))
        return redirect('users')
    user = User.objects.get(username=user_name)
    if request.method == "POST":
        form = AdminEditForm(request.POST, instance=user)
        if form.is_valid():
            new_email = form.cleaned_data['new_email']
            new_password = form.cleaned_data['new_password']
            if new_email != user.email:
                user.email = new_email
                user.save(update_fields=['email'])
                messages.success(request, _(f"Adres email użytkownika {user.username} został zaktualizowany."))
            if new_password:
                user.set_password(new_password)
                update_session_auth_hash(request, user)
                user.save(update_fields=['password'])
                messages.success(request, _(f"Hasło użytkownika {user.username} zostało zaktualizowane."))
            return redirect('users')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, _(f"Błąd w polu '{field}': {error}"))

    else:
        initial_email = user.email
        form = AdminEditForm(instance=user, initial={'new_email': initial_email})
    return render(request, 'movies_collections/edit_user.html', {'form': form})


def user_delete(request, user_name):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('index')
    if user_name is None:
        messages.info(request, _("Nie ma takiego użytkownika"))
        return redirect('users')

    user_to_delete = User.objects.get(username=user_name)
    user_to_delete.delete()
    messages.info(request, _(f"Użytkownik '{user_name}' został pomyślnie usunięty"))
    return redirect('users')


# Views about movies below_________________________________

def search_movies(request):
    if request.method == "POST":
        title = request.POST['title']
        if not title:
            title = request.session['title']
            if not title:
                messages.info(request, _('Proszę podać tytuł'))
                return redirect("index")
        try:
            response = requests.get(f'https://search.imdbot.workers.dev/?q={title}')
            if response.status_code != requests.codes.ok:
                messages.info(request, _(f"Nie można połączyć z bazą danych, kod błędu: {response.status_code}"))
                return render(request, 'movies_collections/search_movies.html', {"user": request.user})
            else:
                data = response.json()
                list_of_searched_films = []
                request.session['title'] = title
                for movie in data['description']:
                    list_of_searched_films.append(movie)
                transformed_films = []
                for film in list_of_searched_films:
                    transformed_film = {
                        'IMDB_ID': film.get('#IMDB_ID'),
                        'TITLE': film.get('#TITLE'),
                        'YEAR': film.get('#YEAR'),
                        'IMG_POSTER': film.get('#IMG_POSTER')
                    }
                    transformed_films.append(transformed_film)
                return render(request, 'movies_collections/search_movies.html',
                              {"user": request.user, "transformed_films": transformed_films})
        except Exception as e:
            return JsonResponse(_({f"Błąd'{e}'"}))

    if request.method == "GET":
        return render(request, 'movies_collections/search_movies.html', {"user": request.user})


def movie_details(request, movie_id):
    title = request.session['title']
    if title is None:
        redirect("index")
    response = requests.get(f'https://search.imdbot.workers.dev/?tt={movie_id}')
    if response.status_code != requests.codes.ok:
        messages.info(request, _(f"Nie można połączyć z bazą danych, kod błędu: {response.status_code}"))
    else:
        movie = response.json()
        return render(request, "movies_collections/movie_details.html", {"movie": movie, "title": title})


def save_movie(request, movie_id):
    if not request.user.is_authenticated:
        return redirect('login_user')
    movie_id = str(movie_id)
    record = FavouritesMovies.objects.filter(user=request.user, movie_id=movie_id).exists()
    if record:
        messages.info(request, _("Ten film już jest zapisany w bibliotece 'Ulubione'"))
    else:
        FavouritesMovies.objects.create(user=request.user, movie_id=movie_id)
        messages.info(request, _("Film zapisano pomyślnie w bibliotece 'Ulubione'"))
    return redirect('movie_details', movie_id=movie_id)


def favourites(request):
    fav_movies = FavouritesMovies.objects.filter(user=request.user)
    list_of_film_id = [movie.movie_id for movie in fav_movies]
    film_collection = []
    for film in list_of_film_id:
        response = requests.get(f'https://search.imdbot.workers.dev/?tt={film}')
        message = None
        if response.status_code != requests.codes.ok:
            message = _(f"Nie można połączyć z bazą danych, kod błędu: {response.status_code}")
        if message is not None:
            messages.info(request, message)
        else:
            movie = response.json()
            film_collection.append(movie)
    return render(request, 'movies_collections/favourites.html', {'film_collection': film_collection})


def movie_delete(request, movie_id):
    if not request.user.is_authenticated:
        return redirect('login_user')
    FavouritesMovies.objects.filter(user=request.user, movie_id=movie_id).delete()
    messages.info(request, _(f"Film został pomyślnie usunięty z ulubionych"))
    return redirect('favourites')


def about(request):
    return render(request, 'movies_collections/about.html')

from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View
from mysite import settings
from .api import MoviesAPI, MovieDetailsAPI, FavouritesService
from django.utils.translation import gettext as _, activate
from .services import *


class IndexView(View):
    template_name = 'movies_collections/index.html'

    def get(self, request):
        user = request.user
        context = {'user': user}
        return render(request, self.template_name, context)


class ChangeLanguageView(View):
    def get(self, request, language_code):
        if language_code in [lang[0] for lang in settings.LANGUAGES]:
            request.session['django_language'] = language_code
            activate(language_code)
            return redirect(reverse('index'))
        else:
            return redirect(reverse('index'))


class LoginUserView(View):
    template_name = 'movies_collections/login.html'
    user_service = UserService()

    def get(self, request):
        return render(request, 'movies_collections/login.html')

    def post(self, request):
        username = request.POST.get('user_name')
        password = request.POST.get('user_pass')
        user = self.user_service.authenticate_user(request, username, password)

        if user is not None:
            self.user_service.login_user(request, user, username)
            return redirect('index')
        else:
            login_failed_data = self.user_service.login_failed_data(request, request.user)
            return render(request, self.template_name, login_failed_data)


class LogoutUserView(View):
    template_name = 'movies_collections/index.html'

    def get(self, request):
        user_service = UserService()
        logout_data = user_service.logout_user_data(request)
        return render(request, self.template_name, logout_data)


class NewUserView(View):
    template_name = 'movies_collections/new_user.html'
    user_service = UserService()

    def get(self, request):
        return render(request, self.template_name, self.user_service.get_context_data(request))

    def post(self, request):
        form = UserRegistrationForm(request.POST)
        registration_data = self.user_service.process_registration_data(request, form)

        if registration_data['registration_successful']:
            return redirect('index')
        else:
            return render(request, self.template_name, registration_data)


class MyProfileView(View):
    template_name = 'movies_collections/my_profile.html'
    my_profile_service = MyProfileService()

    def get(self, request):
        return render(request, self.template_name, self.my_profile_service.get_context_data(request))

    def post(self, request):
        form = UserEditForm(request.POST, instance=request.user)
        update_data = self.my_profile_service.update_user_data(request, form)

        if update_data['update_successful']:
            return redirect('my_profile')
        else:
            return render(request, self.template_name, update_data)


class UsersView(View):
    template_name = 'movies_collections/users.html'
    users_view_service = UsersViewService()

    def get(self, request):
        user_list = self.users_view_service.handle_get_request(request)

        if user_list is not None:
            context_data = self.users_view_service.get_context_data(user_list)
            return render(request, self.template_name, context_data)
        else:
            return redirect('index')

    def post(self, request):
        return redirect('users')


class UserStatusChangeView(View):
    user_service = UserEdit()

    def get(self, request, action, user_name):
        user = User.objects.get(username=user_name)

        if self.user_service.authorize_users(request.user):
            return redirect('index')

        self.user_service.perform_action(user, action)
        return redirect('users')


class EditUserView(View):
    template_name = 'movies_collections/edit_user.html'
    user_service = UserEdit()

    def get(self, request, user_name):
        if not request.user.is_authenticated or not request.user.is_superuser:
            return redirect('index')

        user = self.user_service.get_user_instance(user_name)
        if not user:
            messages.info(request, _("Nie ma takiego użytkownika"))
            return redirect('users')

        form = self.user_service.create_edit_form(user)
        return render(request, self.template_name, {'form': form})

    def post(self, request, user_name):
        if not request.user.is_authenticated or not request.user.is_superuser:
            return redirect('index')

        form_data = request.POST
        edited, errors, user = self.user_service.process_edit_user(request, user_name, form_data)

        if edited:
            messages.success(request, _("Użytkownik {username} został zaktualizowany.").format(username=user.username))
            return redirect('users')

        for field, field_errors in errors.items():
            for error in field_errors:
                messages.error(request, _("Błąd w polu '{field}': {error}").format(field=field, error=error))

        form = self.user_service.create_edit_form(user, form_data)
        return render(request, self.template_name, {'form': form})


class UserDeleteView(View):
    def post(self, request, user_name):
        if not request.user.is_authenticated or not request.user.is_superuser:
            return redirect('index')

        user_service = UsersViewService()
        deleted_user_name = user_service.delete_user(user_name)

        messages.info(request, _("Użytkownik '{username}' został pomyślnie usunięty").format(username=deleted_user_name))
        return redirect('users')


class SearchMoviesView(View):
    template_name = 'movies_collections/search_movies.html'
    movies_api = MoviesAPI()

    def get(self, request):
        return render(request, self.template_name, {"user": request.user})

    def post(self, request):
        title = request.POST.get('title', '').strip()

        if not title:
            try:
                title = request.session['title']
            except:
                messages.info(request, _('Proszę podać tytuł'))
                return redirect("index")

        movies_data, error_message = self.movies_api.search_movies(title)

        if error_message:
            messages.info(request, error_message)
            return render(request, self.template_name, {"user": request.user})

        request.session['title'] = title

        return render(request, self.template_name, {"user": request.user, "transformed_films": movies_data})


class MovieDetailsView(View):
    template_name = 'movies_collections/movie_details.html'
    movie_details_api = MovieDetailsAPI()

    def get(self, request, movie_id):
        title = request.session.get('title')

        if title is None:
            return redirect("index")

        movie_data, error_message = self.movie_details_api.get_movie_details(movie_id)

        if movie_data:
            transformed_movie = self.movie_details_api.transform_movie_data(movie_data)
            return render(request, self.template_name, {"movie": transformed_movie, "title": title})
        else:
            messages.info(request, _("Błąd podczas pobierania danych z API: {error}").format(error=error_message))
            return render(request, self.template_name, {"title": title})


class SaveMovieView(View):
    favourites_service = FavouritesService()

    def get(self, request, movie_id):
        if not request.user.is_authenticated:
            return redirect('login_user')

        response_message = self.favourites_service.save_movie(request.user, movie_id)
        messages.info(request, response_message)

        return redirect('movie_details', movie_id=movie_id)


class FavouritesView(View):
    template_name = 'movies_collections/favourites.html'
    favourites_service = FavouritesService()

    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('login_user')

        film_collection = self.favourites_service.get_favourite_movies(request.user, request)
        return render(request, self.template_name, {'film_collection': film_collection})


class MovieDeleteView(View):
    favourites_service = FavouritesService()

    def get(self, request, movie_id):
        if not request.user.is_authenticated:
            return redirect('login_user')

        self.favourites_service.delete_movie(request.user, movie_id, request)

        return redirect('favourites')


class AboutView(View):
    template_name = 'movies_collections/about.html'

    def get(self, request):
        return render(request, self.template_name)

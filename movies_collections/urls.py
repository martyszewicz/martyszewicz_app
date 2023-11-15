from django.urls import path
from .views import *



urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('login_user/', LoginUserView.as_view(), name='login_user'),
    path('new_user/', NewUserView.as_view(), name='new_user'),
    path('users/', UsersView.as_view(), name='users'),
    path('user_delete/<str:user_name>/', UserDeleteView.as_view(), name='user_delete'),
    path('about/', AboutView.as_view(), name='about'),
    path('search_movies/', SearchMoviesView.as_view(), name='search_movies'),
    path('logout_user/', LogoutUserView.as_view(), name='logout_user'),
    path('favourites/', FavouritesView.as_view(), name='favourites'),
    path('my_profile/', MyProfileView.as_view(), name='my_profile'),
    path('movie_details/<movie_id>/', MovieDetailsView.as_view(), name='movie_details'),
    path('save_movie/<movie_id>/', SaveMovieView.as_view(), name='save_movie'),
    path('movie_delete/<movie_id>/', MovieDeleteView.as_view(), name='movie_delete'),
    path('user_status_change/<str:action>/<str:user_name>/', UserStatusChangeView.as_view(), name='user_status_change'),
    path('edit_user/<str:user_name>/', EditUserView.as_view(), name='edit_user'),
    path('my_profile/', MyProfileView.as_view(), name='my_profile'),
    path('change_language/<str:language_code>/', ChangeLanguageView.as_view(), name='change_language'),
    ]


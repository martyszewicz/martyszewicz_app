
from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('login_user/', views.login_user, name='login_user'),
    path('new_user/', views.new_user, name='new_user'),
    path('users/', views.users, name='users'),
    path('user_delete/<str:user_name>/', views.user_delete, name='user_delete'),
    path('about/', views.about, name='about'),
    path('search_movies/', views.search_movies, name='search_movies'),
    path('logout_user/', views.logout_user, name='logout_user'),
    path('favourites/', views.favourites, name='favourites'),
    path('my_profile/', views.my_profile, name='my_profile'),
    path('movie_details/<movie_id>/', views.movie_details, name='movie_details'),
    path('save_movie/<movie_id>/', views.save_movie, name='save_movie'),
    path('movie_delete/<movie_id>/', views.movie_delete, name='movie_delete'),
    path('user_status_change/<str:action>/<str:user_name>/', views.user_status_change, name='user_status_change'),
    path('edit_user/<str:user_name>/', views.edit_user, name='edit_user'),
    path('user_delete/<str:user_name>/', views.user_delete, name='user_delete'),
    path('my_profile/', views.my_profile, name='my_profile'),
    path('change_language/<str:language_code>/', views.change_language, name='change_language'),
    ]


from django.urls import path
from . import views

app_name = "coffee_machine"
urlpatterns = [
    path('', views.coffee_machine, name='coffee_machine'),
    ]
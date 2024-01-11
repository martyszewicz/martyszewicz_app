import pdb

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views import View
from .models import *
from .forms import NewGameForm
from django.contrib.auth import login


class HomeView(View):
    template_name = 'tictactoe/home.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        button_clicked = request.POST.get('button_clicked', '')
        if button_clicked == 'new_game':
            return redirect('new_game')
        elif button_clicked == 'join_game':
            return redirect('join_game')
        elif button_clicked == 'single_player':
            return render(request, "tictactoe/single_player.html")

        messages.info(request, 'Something goes wrong, please try again')
        return render(request, self.template_name)


class NewGameView(View):
    template_name = 'tictactoe/new_game.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        form = NewGameForm(request.POST)
        if form.is_valid():
            username = request.POST.get('username')
            room_name = request.POST.get('room_name')
            is_private = bool(form.cleaned_data.get('is_private', False))
            password = request.POST.get('password')

            if not is_private:
                password = ""

            if is_private and not password:
                messages.error(request, "Please provide a password to make a game private.")
                form = NewGameForm()
                return render(request, 'tictactoe/new_game.html', {'form': form})

            existing_game = TictactoeRoom.objects.filter(room_name=room_name).first()
            if existing_game:
                messages.info(request, "Room code already exists. Please choose a different one.")
                form = NewGameForm()
                return render(request, 'tictactoe/new_game.html', {'form': form})

            user_exists = User.objects.filter(username=username).exists()

            if user_exists:
                messages.info(request, "A user with this name already exists. Please choose a different one.")
                form = NewGameForm()
                return render(request, 'tictactoe/new_game.html', {'form': form})
            user = User.objects.create_user(username)
            login(request, user)
            game = TictactoeRoom(game_creator=user, room_name=room_name, is_private=is_private, password=password)
            game.save()
            return redirect('multi_player/' + room_name)
        else:
            form = NewGameForm()

        return render(request, 'tictactoe/new_game.html', {'form': form})


class JoinGameView(View):
    template_name = 'tictactoe/join_game.html'

    def get(self, request):
        games = TictactoeRoom.objects.filter(game_opponent=None)
        return render(request, self.template_name, {'games': games})

    def post(self, request):
        username = request.POST.get('username')
        room_name = request.POST.get('room_name')
        password = request.POST.get('password')

        if not username:
            messages.error(request, "Please provide a username.")
            return redirect('join_game')
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists. Please choose a different one.")
            return redirect('join_game')
        game = TictactoeRoom.objects.filter(room_name=room_name).first()
        if game.game_opponent is not None:
            messages.info(request, "Game already started.")
            return redirect('join_game')
        if game is None:
            messages.info(request, "Room code not found or game already started.")
            return redirect('join_game')

        if game.is_private:
            if not password:
                messages.info(request, "Please provide a password")
                return redirect('join_game')

            if password != game.password:
                messages.info(request, "Wrong password")
                return redirect('join_game')
        user = User.objects.create_user(username)
        login(request, user)
        game.game_opponent = user
        game.save()
        return redirect('multi_player/' + room_name)


class Multi_player(View):
    template_name_multiplayer = 'tictactoe/multi_player.html'

    def get(self, request, room_name=None):
        username = request.user.username if request.user.is_authenticated else None

        if not username:
            return HttpResponse("Unauthorized", status=401)

        try:
            game = TictactoeRoom.objects.get(room_name=room_name)
        except TictactoeRoom.DoesNotExist:
            return HttpResponse("Room not found", status=404)

        return render(request, self.template_name_multiplayer, {'room_name': room_name, 'username': username,
                    'game': game, 'game_creator': game.game_creator, 'game_opponent': game.game_opponent})


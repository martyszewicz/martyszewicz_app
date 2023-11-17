from django.shortcuts import render, redirect
from django.contrib import messages
from django.views import View
from .models import *
from .forms import NewGameForm

class HomeView(View):
    template_name = 'battleships/home.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        if 'join_game' in request.POST:
            return redirect('join_game')
        elif 'new_game' in request.POST:
            return redirect('new_game')

        messages.info(request, 'Something goes wrong, please try again')
        return render(request, self.template_name)


class NewGameView(View):
    template_name = 'battleships/new_game.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        form = NewGameForm(request.POST)
        if form.is_valid():
            username = request.POST.get('username')
            room_code = request.POST.get('room_code')
            is_private = request.POST.get('is_private')
            password = request.POST.get('password')

            if is_private:
                if not password:
                    messages.error(request, "Please provide a password to make a game private.")
                    form = NewGameForm()
                    return render(request, 'battleships/new_game.html', {'form': form})

            existing_game = Game.objects.filter(room_code=room_code).first()
            if existing_game:
                messages.info(request, "Room code already exists. Please choose a different one.")
                form = NewGameForm()
                return render(request, 'battleships/new_game.html', {'form': form})

            game = Game(game_creator=username, room_code=room_code, is_private=is_private, password=password)
            game.save()
            return redirect('/play/' + room_code + '?username=' + username)
        else:
            form = NewGameForm()

        return render(request, 'battleships/new_game.html', {'form': form})


class JoinGameView(View):
    template_name = 'battleships/join_game.html'

    def get(self, request):
        games = Game.objects.filter(status=['waiting'])
        return render(request, self.template_name, {'games': games})

    def post(self, request):
        username = request.POST.get('username')
        room_code = request.POST.get('room_code')
        password = request.POST.get('password')

        if not username:
            messages.error(request, "Please provide a username.")
            return redirect('join_game')

        if Game.objects.filter(game_creator=username).exists():
            messages.error(request, "Username already taken. Please choose a different one.")
            return redirect('join_game')

        game = Game.objects.filter(room_code=room_code, status='waiting').first()

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

        game.game_opponent = username

        return redirect('battleships/play/' + room_code + '?username=' + username)


class PlayView(View):
    template_name = 'play.html'

    def get(self, request, room_code):
        username = request.GET.get('username')
        context = {'room_code': room_code, 'username': username}
        return render(request, self.template_name, context)

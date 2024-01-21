from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views import View
from .models import *
from .forms import NewGameForm
from django.contrib.auth import login
from django.utils.translation import gettext as _, activate
from mysite import settings
from django.urls import reverse


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

        messages.info(request, _('Coś poszło nie tak, spróbuj ponownie'))
        return render(request, self.template_name)


class ChangeLanguageView(View):
    def get(self, request, language_code):
        if language_code in [lang[0] for lang in settings.LANGUAGES]:
            request.session['django_language'] = language_code
            activate(language_code)
            return redirect(reverse('home'))
        else:
            return redirect(reverse('home'))


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
                messages.error(request, _("Aby utworzyć prywatną grę proszę utworzyć hasło"))
                form = NewGameForm()
                return render(request, 'tictactoe/new_game.html', {'form': form})

            existing_game = TictactoeRoom.objects.filter(room_name=room_name).first()
            if existing_game:
                messages.info(request, _("Ta nazwa pokoju jest już zajęta. Podaj inną nazwę"))
                form = NewGameForm()
                return render(request, 'tictactoe/new_game.html', {'form': form})

            user_exists = User.objects.filter(username=username).exists()

            if user_exists:
                messages.info(request, _("Ten pseudonim już jest zajęty. Podaj inny pseudonim"))
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
            messages.error(request, _("Proszę wprowadzić pseudonim"))
            return redirect('join_game')
        if User.objects.filter(username=username).exists():
            messages.error(request, _("Ten pseudonim już jest zajęty. Podaj inny pseudonim"))
            return redirect('join_game')
        game = TictactoeRoom.objects.filter(room_name=room_name).first()
        if game.game_opponent is not None:
            messages.info(request, _("Gra już się rozpoczęła"))
            return redirect('join_game')
        if game is None:
            messages.info(request, _("Nie znaleziono pokoju o tej nazwie lub gra już się rozpoczęła"))
            return redirect('join_game')

        if game.is_private:
            if not password:
                messages.info(request, _("Proszę podać hasło"))
                return redirect('join_game')

            if password != game.password:
                messages.info(request, _("Hasło nieprawidłowe"))
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


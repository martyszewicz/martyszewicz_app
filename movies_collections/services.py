from django.contrib.auth import update_session_auth_hash, authenticate, login, logout, get_user_model
from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext as _
from movies_collections.forms import UserRegistrationForm, UserEditForm, AdminEditForm


class UserService:
    def authenticate_user(self, request, username, password):
        user = authenticate(request, username=username, password=password)
        return user

    def login_user(self, request, user, username):
        login(request, user)
        messages.info(request, _("Witaj {username}!").format(username=username))

    def login_failed_data(self, request, user):
        messages.info(request, _("Błąd logowania, spróbuj ponownie"))
        return {'login_failed': True, 'user': user}

    def logout_user_data(self, request):
        if request.user.is_authenticated:
            logout(request)
            messages.info(request, _("Wylogowałeś się poprawnie"))
        return {'logout_successful': True}

    def get_context_data(self, request):
        form = UserRegistrationForm()
        return {'form': form, 'user': request.user}

    def process_registration_data(self, request, form):
        if form.is_valid():
            form.save()
            messages.info(request, _("Użytkownik {username} został zarejestrowany").format(username=form.cleaned_data['username']))
            return {'registration_successful': True}
        else:
            errors = [error for field, errors in form.errors.items() for error in errors]
            for error in errors:
                messages.info(request, _('Błąd: {error}').format(error=error))
            return {'registration_successful': False, 'form': form, 'user': request.user}


class MyProfileService:
    def get_context_data(self, request):
        initial_email = request.user.email
        form = UserEditForm(instance=request.user, initial={'new_email': initial_email})
        return {'form': form}

    def update_user_data(self, request, form):
        if form.is_valid():
            current_password = form.cleaned_data['current_password']
            new_email = form.cleaned_data['new_email']
            new_password = form.cleaned_data['new_password']

            if request.user.check_password(current_password):
                if new_email:
                    request.user.email = new_email
                    request.user.save(update_fields=['email'])

                if new_password:
                    request.user.set_password(new_password)
                    update_session_auth_hash(request, request.user)
                    request.user.save(update_fields=['password'])

                messages.success(request, _("Dane użytkownika zostały zaktualizowane."))
                return {'update_successful': True}
            else:
                messages.error(request, _("Aktualne hasło jest nieprawidłowe."))
        else:
            errors = [error for field, errors in form.errors.items() for error in errors]
            for error in errors:
                messages.error(request, _("Błąd: {error}").format(error=error))

        return {'update_successful': False, 'form': form}


class UsersViewService:
    def get_user_list(self):
        return get_user_model().objects.all()

    def get_context_data(self, user_list):
        return {'users': user_list}

    def is_user_authorized(self, request):
        user = request.user
        return user.is_authenticated and user.is_superuser

    def handle_get_request(self, request):
        if self.is_user_authorized(request):
            return self.get_user_list()
        else:
            return None

    def delete_user(self, user_name):
        user_to_delete = get_object_or_404(User, username=user_name)
        user_to_delete.delete()
        return user_name


class UserEdit:

    def get_user_instance(self, user_name):
        return User.objects.filter(username=user_name).first()

    def get_initial_form_data(self, user):
        return {'new_email': user.email}

    def create_edit_form(self, user, form_data=None):
        return AdminEditForm(instance=user, initial=self.get_initial_form_data(user), data=form_data)

    def edit_user(self, request, user, form):
        if form.is_valid():
            new_email = form.cleaned_data['new_email']
            new_password = form.cleaned_data['new_password']

            if new_email != user.email:
                user.email = new_email
                user.save(update_fields=['email'])
                return True, []

            if new_password:
                user.set_password(new_password)
                update_session_auth_hash(request, user)
                user.save(update_fields=['password'])
                return True, []

        return False, form.errors

    def process_edit_user(self, request, user_name, form_data):
        user = self.get_user_instance(user_name)
        if not user:
            return False, _("Nie ma takiego użytkownika"), None

        form = self.create_edit_form(user, form_data)
        edited, errors = self.edit_user(request, user, form)

        return edited, errors, user

    def authorize_users(self, user):
        return not user.is_authenticated or not user.is_superuser

    def perform_action(self, user, action):
        if action == 'status_change':
            user.is_active = not user.is_active
        elif action == 'admin_change':
            user.is_superuser = not user.is_superuser

        user.save()




from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm


class UserRegistrationForm(UserCreationForm):

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not username:
            raise forms.ValidationError("Pole 'nazwa użytkownika' nie może być puste")
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError(f"Użytkownik o nazwie '{username}' już istnieje")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise forms.ValidationError("Pole 'email' nie może być puste")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(f"Adres email '{email}' jest już wykorzystany")
        return email

    def clean_password(self):
        password = self.cleaned_data.get('password1')
        if not password:
            raise forms.ValidationError("Pole 'hash' nie może być puste")
        return password


class UserEditForm(UserChangeForm):
    current_password = forms.CharField(widget=forms.PasswordInput(), label='Aktualne hasło', required=True)
    new_email = forms.EmailField(label='Nowy adres email', required=False)
    new_password = forms.CharField(widget=forms.PasswordInput(), label='Nowe hasło', required=False)
    confirm_new_password = forms.CharField(widget=forms.PasswordInput(), label='Potwierdź nowe hasło', required=False)

    class Meta:
        model = User
        fields = ('email',)

    error_messages = {
        'email': None,
    }

    def clean_new_email(self):
        new_email = self.cleaned_data.get('new_email')

        if new_email == '':
            return self.instance.email if self.instance.email else None

        if User.objects.filter(email=new_email).exclude(username=self.instance.username).exists():
            raise forms.ValidationError("Adres email jest już używany przez innego użytkownika.")

        return new_email

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_new_password = cleaned_data.get('confirm_new_password')

        if new_password and new_password != confirm_new_password:
            raise forms.ValidationError("Nowe hasła nie pasują do siebie")

        return cleaned_data


class AdminEditForm(forms.ModelForm):
    new_email = forms.EmailField(label='Nowy adres email', required=False)
    new_password = forms.CharField(widget=forms.PasswordInput(), label='Nowe hasło', required=False)
    confirm_new_password = forms.CharField(widget=forms.PasswordInput(), label='Potwierdź nowe hasło', required=False)

    class Meta:
        model = User
        fields = ['email']

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_new_password = cleaned_data.get('confirm_new_password')

        if new_password and new_password != confirm_new_password:
            raise forms.ValidationError("Nowe hasła nie pasują do siebie")

        return cleaned_data

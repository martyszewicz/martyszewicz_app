from django import forms


class NewGameForm(forms.Form):
    username = forms.CharField(label='Username', max_length=100)
    room_code = forms.CharField(label='Room Code', max_length=100)
    is_private = forms.BooleanField(label='Is Private', required=False)
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
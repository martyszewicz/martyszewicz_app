from django import forms


class NewGameForm(forms.Form):
    username = forms.CharField(label='username', max_length=100)
    room_name = forms.CharField(label='room_name', max_length=100)
    is_private = forms.BooleanField(label='is_private', required=False, initial=False)
    password = forms.CharField(label='password',required=False, widget=forms.PasswordInput)
from django import forms



class User_choice(forms.Form):
    user_choice = forms.CharField()

class Budget_change(forms.Form):
    budget_change = forms.FloatField()

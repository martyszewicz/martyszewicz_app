from django.shortcuts import render


def homepage(request):
    return render(request, 'mysite/homepage.html')
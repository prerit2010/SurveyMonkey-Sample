from django.shortcuts import render
from django.http import HttpResponse

from .models import Users


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

# Create your views here.

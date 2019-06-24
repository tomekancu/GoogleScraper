from django.shortcuts import render
from django.http import HttpResponse
import logging


# Create your views here.


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


def index2(request):
    logging.error("index")
    return render(request, 'index.html', {"app_title": "GoogleScraper"})

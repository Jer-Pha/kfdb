from django.http import HttpResponse
from django.shortcuts import render


def host_home(request):
    return HttpResponse()


def host_page(request, type):
    return HttpResponse()


def host_detail(request, type, name):
    return HttpResponse()

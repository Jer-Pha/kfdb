"""URL configuration for KFDB channels."""

from django.urls import path

from .views import channel_home, channel_page

urlpatterns = [
    path("channels/", channel_home, name="channel_home"),
    path("<slug:channel>/", channel_page, name="channel_page"),
]

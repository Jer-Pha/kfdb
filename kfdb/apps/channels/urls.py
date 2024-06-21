"""URL configuration for KFDB channels."""

from django.urls import path

from .views import channels_home, channel_page

urlpatterns = [
    path("channels/", channels_home, name="channels_home"),
    path("<slug:channel>/", channel_page, name="channel_page"),
]

"""URL configuration for KFDB videos."""

from django.urls import path

from .views import ChannelPageView

urlpatterns = [
    path("videos/", ChannelPageView.as_view(), name="videos_home"),
]

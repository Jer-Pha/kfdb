"""URL configuration for KFDB videos."""

from django.urls import path

from .views import get_video_details, videos_home

urlpatterns = [
    path("videos/", videos_home, name="videos_home"),
    path("video/details", get_video_details, name="load_video_details"),
]

"""URL configuration for KFDB videos."""

from django.urls import path

from .views import AllVideosView, UpdateVideosView

urlpatterns = [
    path("videos/", AllVideosView.as_view(), name="videos_home"),
    path("videos/update/", UpdateVideosView.as_view(), name="update_videos"),
]

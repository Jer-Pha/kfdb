"""URL configuration for KFDB edits."""

from django.urls import path

from .views import (
    EditChannelView,
    EditHostView,
    EditShowView,
    EditVideoView,
)

urlpatterns = [
    path("edit/channel", EditChannelView.as_view(), name="edit_channel"),
    path("edit/host", EditHostView.as_view(), name="edit_host"),
    path("edit/show", EditShowView.as_view(), name="edit_show"),
    path("edit/video", EditVideoView.as_view(), name="edit_video"),
]

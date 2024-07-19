"""URL configuration for KFDB videos."""

from django.urls import path

from .views import (
    AllVideosView,
    UpdateVideosView,
    VideoBlurbView,
    VideoEmbedView,
    VideoDetailsView,
)

urlpatterns = [
    path("videos/", AllVideosView.as_view(), name="videos_home"),
    path("videos/update/", UpdateVideosView.as_view(), name="update_videos"),
    path("get/video-blurb", VideoBlurbView.as_view(), name="get_video_blurb"),
    path("get/video-embed", VideoEmbedView.as_view(), name="get_video_embed"),
    path(
        "get/video-details",
        VideoDetailsView.as_view(),
        name="get_video_details",
    ),
]

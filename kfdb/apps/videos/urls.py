"""URL configuration for KFDB videos."""

from django.urls import path
from django.views.generic import TemplateView

from .views import (
    AllVideosChartsView,
    AllVideosView,
    BirthdayGamesDaily,
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
    path("videos/charts", AllVideosChartsView.as_view(), name="videos_charts"),
    path(
        "kfgd-birthdays/",
        TemplateView.as_view(template_name="videos/kfgd-birthdays.html"),
    ),
    path(
        "get/kfgd-birthdays",
        BirthdayGamesDaily.as_view(),
        name="get_kfgd_birthdays",
    ),
]

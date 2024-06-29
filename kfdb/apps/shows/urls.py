"""URL configuration for KFDB shows."""

from django.urls import path

from .views import ShowPageView
from django.views.generic.base import RedirectView


urlpatterns = [
    path(
        "shows/",
        RedirectView.as_view(permanent=True, pattern_name="channel_page"),
        name="show_home",
    ),
    path("s/<slug:show>/", ShowPageView.as_view(), name="show_page"),
]

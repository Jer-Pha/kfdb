"""URL configuration for KFDB shows."""

from django.urls import path

from .views import show_page
from django.views.generic.base import RedirectView


urlpatterns = [
    path(
        "shows/",
        RedirectView.as_view(permanent=True, pattern_name="channel_page"),
        name="show_home",
    ),
    path("s/<slug:show>/", show_page, name="show_page"),
]

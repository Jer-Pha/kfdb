"""URL configuration for the KFDB project."""

from django.conf import settings
from django.urls import include, path


urlpatterns = [
    path("", include("apps.core.urls")),
    path("channels/", include("apps.channels.urls")),
    path("videos/", include("apps.videos.urls")),
    path("hosts/", include("apps.hosts.urls")),
    path("shows/", include("apps.shows.urls")),
]

if settings.DEBUG:  # pragma: no cover
    urlpatterns += [
        path("__debug__/", include("debug_toolbar.urls")),
    ]

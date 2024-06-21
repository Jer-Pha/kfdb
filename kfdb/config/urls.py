"""URL configuration for the KFDB project."""

from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path


urlpatterns = [
    path("", include("apps.core.urls")),
    path("", include("apps.channels.urls")),
    path("", include("apps.videos.urls")),
    path("", include("apps.hosts.urls")),
    path("", include("apps.shows.urls")),
]

if settings.DEBUG:  # pragma: no cover
    urlpatterns = [
        path("__debug__/", include("debug_toolbar.urls")),
    ] + urlpatterns

    urlpatterns += static("/media/", document_root=settings.MEDIA_ROOT)

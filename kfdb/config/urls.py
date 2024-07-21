"""URL configuration for the KFDB project."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import index, sitemap
from django.urls import include, path

from .sitemaps import (
    ChannelSitemap,
    CoreViewSitemap,
    ShowSitemap,
    HostSitemap,
    StaticViewSitemap,
)

sitemaps = {
    "core": CoreViewSitemap,
    "hosts": HostSitemap,
    "shows": ShowSitemap,
    "channels": ChannelSitemap,
    "static": StaticViewSitemap,
}


urlpatterns = [
    path("", include("apps.core.urls")),
    path("", include("apps.channels.urls")),
    path("", include("apps.edits.urls")),
    path("", include("apps.hosts.urls")),
    path("", include("apps.shows.urls")),
    path("", include("apps.videos.urls")),
]

# Sitemaps
urlpatterns += [
    path(
        "sitemap.xml",
        index,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.index",
    ),
    path(
        "sitemap-<section>.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
]

if settings.DEBUG:  # pragma: no cover
    urlpatterns = [
        path("__debug__/", include("debug_toolbar.urls")),
    ] + urlpatterns

    urlpatterns += static("/media/", document_root=settings.MEDIA_ROOT)

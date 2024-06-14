"""URL configuration for kfdb project."""

from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.channels.views import ChannelViewSet
from apps.episodes.views import EpisodeViewSet, upload_view  # Temporary
from apps.hosts.views import HostViewSet
from apps.shows.views import ShowViewSet

router = DefaultRouter()
router.register("channels", ChannelViewSet, basename="channels")
router.register("episodes", EpisodeViewSet, basename="episodes")
router.register("hosts", HostViewSet, basename="hosts")
router.register("shows", ShowViewSet, basename="shows")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api-auth/", include("rest_framework.urls")),
    path("api/", include(router.urls)),
    path("temp/upload/", upload_view),  # Temporary
]

if settings.DEBUG:  # pragma: no cover
    urlpatterns += [
        path("__debug__/", include("debug_toolbar.urls")),
    ]

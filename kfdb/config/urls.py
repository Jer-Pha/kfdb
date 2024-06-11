"""URL configuration for kfdb project."""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api-auth/", include("rest_framework.urls")),
    path("channels/", include("apps.channels.urls")),
    path("episodes/", include("apps.episodes.urls")),
    path("hosts/", include("apps.hosts.urls")),
    path("shows/", include("apps.shows.urls")),
]

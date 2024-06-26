"""URL configuration for core KFDB features."""

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from django.contrib import admin
from django.templatetags.static import static
from django.urls import include, path
from django.views.generic import RedirectView, TemplateView
from rest_framework.routers import DefaultRouter

from .views import build_filter, homepage, update_index_stats, update_theme
from apps.channels.viewsets import ChannelViewSet
from apps.hosts.viewsets import HostViewSet
from apps.shows.viewsets import ShowViewSet
from apps.videos.viewsets import VideoViewSet
from apps.videos.views import upload_view  # Temporary

router = DefaultRouter()
router.register("channels", ChannelViewSet, basename="channels")
router.register("hosts", HostViewSet, basename="hosts")
router.register("shows", ShowViewSet, basename="shows")
router.register("videos", VideoViewSet, basename="videos")


urlpatterns = [
    path(
        "", TemplateView.as_view(template_name="core/hero.html"), name="hero"
    ),
    path("home/", homepage, name="index"),
    path("load-stats", update_index_stats, name="load_stats"),
    path("change-theme", update_theme, name="update_theme"),
    path("build-filter", build_filter, name="build_filter"),
    path("kfdb-admin/", admin.site.urls, name="admin"),
    path("temp/upload/", upload_view),  # Temporary
]

# Favicon urls
urlpatterns += [
    path(
        "android-chrome-192x192.png",
        RedirectView.as_view(url=static("favicon/android-chrome-192x192.png")),
    ),
    path(
        "android-chrome-512x512.png",
        RedirectView.as_view(url=static("favicon/android-chrome-512x512.png")),
    ),
    path(
        "browserconfig.xml",
        RedirectView.as_view(url=static("favicon/browserconfig.xml")),
    ),
    path(
        "favicon.ico",
        RedirectView.as_view(url=static("favicon/favicon.ico")),
    ),
    path(
        "mstile-150x150.png",
        RedirectView.as_view(url=static("favicon/mstile-150x150.png")),
    ),
]

# API urls
urlpatterns += [
    path("api-auth/", include("rest_framework.urls")),
    path("api/", include(router.urls)),
    # YOUR PATTERNS
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    # Optional UI:
    path(
        "api/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/schema/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
]

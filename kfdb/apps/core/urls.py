"""URL configuration for core KFDB features."""

from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView

from django.contrib import admin
from django.templatetags.static import static
from django.urls import include, path
from django.views.generic import RedirectView, TemplateView
from rest_framework.routers import DefaultRouter

from .views import (
    BuildFilterView,
    HeroStatsView,
    HostCountView,
    UpdateThemeView,
    ShowCountView,
)
from .views import get_news_data
from apps.channels.viewsets import ChannelViewSet
from apps.hosts.viewsets import HostViewSet
from apps.shows.viewsets import ShowViewSet
from apps.videos.viewsets import VideoViewSet

router = DefaultRouter(trailing_slash=False)
router.register("channels", ChannelViewSet, basename="channels")
router.register("hosts", HostViewSet, basename="hosts")
router.register("shows", ShowViewSet, basename="shows")
router.register("videos", VideoViewSet, basename="videos")


urlpatterns = [
    path(
        "", TemplateView.as_view(template_name="core/hero.html"), name="hero"
    ),
    path(
        "home/",
        TemplateView.as_view(template_name="core/index.html"),
        name="index",
    ),
    path(
        "support/",
        TemplateView.as_view(template_name="core/support.html"),
        name="support",
    ),
    path(
        "privacy-policy/",
        TemplateView.as_view(template_name="core/privacy-policy.html"),
        name="privacy_policy",
    ),
    path("load-stats", HeroStatsView.as_view(), name="load_stats"),
    path("host-count", HostCountView.as_view(), name="get_host_count"),
    path("show-count", ShowCountView.as_view(), name="get_show_count"),
    path("change-theme", UpdateThemeView.as_view(), name="update_theme"),
    path("build-filter", BuildFilterView.as_view(), name="build_filter"),
    path("kfdb-admin/", admin.site.urls, name="admin"),
]

# Favicon urls
urlpatterns += [
    path(
        "android-chrome-192x192.png",
        RedirectView.as_view(
            url=static("favicon/android-chrome-192x192.png"),
            permanent=True,
        ),
    ),
    path(
        "android-chrome-512x512.png",
        RedirectView.as_view(
            url=static("favicon/android-chrome-512x512.png"),
            permanent=True,
        ),
    ),
    path(
        "browserconfig.xml",
        RedirectView.as_view(
            url=static("favicon/browserconfig.xml"),
            permanent=True,
        ),
    ),
    path(
        "favicon.ico",
        RedirectView.as_view(
            url=static("favicon/favicon.ico"),
            permanent=True,
        ),
    ),
    path(
        "mstile-150x150.png",
        RedirectView.as_view(
            url=static("favicon/mstile-150x150.png"),
            permanent=True,
        ),
    ),
]

# API urls
urlpatterns += [
    path("api/", include(router.urls)),
    path("api/schema/download", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="api_docs",
    ),
    path(
        "api/news/articles-by-topic",
        get_news_data,
        kwargs={"data_type": "articles-by-topic"},
        name="get_articles_by_topic",
    ),
    path(
        "api/news/articles-by-site",
        get_news_data,
        kwargs={"data_type": "articles-by-site"},
        name="get_articles_by_site",
    ),
    path(
        "api/news/topics",
        get_news_data,
        kwargs={"data_type": "topics"},
        name="get_topics",
    ),
]

# Text files
urlpatterns += [
    path(
        "robots.txt",
        TemplateView.as_view(
            template_name="robots.txt", content_type="text/plain"
        ),
    ),
    path(
        "humans.txt",
        TemplateView.as_view(
            template_name="humans.txt", content_type="text/plain"
        ),
    ),
]

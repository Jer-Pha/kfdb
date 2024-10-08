"""URL configuration for KFDB shows."""

from django.urls import path

from .views import ShowChartsView, ShowPageView, ShowsHomeView


urlpatterns = [
    path("shows/", ShowsHomeView.as_view(), name="shows_home"),
    path("shows/<slug:show>/", ShowPageView.as_view(), name="show_page"),
    path("shows/charts", ShowChartsView.as_view(), name="show_charts"),
]

"""URL configuration for KFDB hosts."""

from django.urls import path

from .views import HostPageView, host_home, host_type


urlpatterns = [
    path("hosts/", host_home, name="host_home"),
    path("h/<slug:type>/", host_type, name="host_type"),
    path(
        "h/<slug:type>/<slug:host>/",
        HostPageView.as_view(),
        name="host_page",
    ),
]

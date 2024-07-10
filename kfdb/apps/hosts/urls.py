"""URL configuration for KFDB hosts."""

from django.urls import path

from .views import (
    HostCrewView,
    HostGuestView,
    HostsHomeView,
    HostPageView,
    HostPartTimerView,
)


urlpatterns = [
    path("hosts/", HostsHomeView.as_view(), name="hosts_home"),
    path("hosts/kf-crew/", HostCrewView.as_view(), name="hosts_crew"),
    path(
        "hosts/part-timers/",
        HostPartTimerView.as_view(),
        name="hosts_part_timers",
    ),
    path("hosts/guests/", HostGuestView.as_view(), name="hosts_guests"),
    path(
        "hosts/<slug:type>/<slug:host>/",
        HostPageView.as_view(),
        name="host_page",
    ),
]

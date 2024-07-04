"""URL configuration for KFDB hosts."""

from django.urls import path

from .views import (
    HostCrewView,
    HostGuestView,
    HostHomeView,
    HostPageView,
    HostPartTimerView,
)


urlpatterns = [
    path("hosts/", HostHomeView.as_view(), name="hosts_home"),
    path("h/kf-crew/", HostCrewView.as_view(), name="hosts_crew"),
    path(
        "h/part-timers/", HostPartTimerView.as_view(), name="hosts_part_timers"
    ),
    path("h/guests/", HostGuestView.as_view(), name="hosts_guests"),
    path(
        "h/<slug:type>/<slug:host>/",
        HostPageView.as_view(),
        name="host_page",
    ),
]

"""URL configuration for KFDB hosts."""

from django.urls import path

from .views import host_detail, host_home, host_page


urlpatterns = [
    path("hosts/", host_home, name="host_home"),
    path("hosts/<slug:type>/", host_page, name="host_page"),
    path("hosts/<slug:type>/<slug:name>/", host_detail, name="host_detail"),
]

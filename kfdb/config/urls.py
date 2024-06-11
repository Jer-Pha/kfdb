"""URL configuration for kfdb project."""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api-auth/", include("rest_framework.urls")),
    path("kfdb/", include("apps.kfdb_api.urls")),
]

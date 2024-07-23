from django.contrib import admin

from .models import Host


@admin.register(Host)
class VideoAdmin(admin.ModelAdmin):
    search_fields = (
        "name",
        "slug",
    )

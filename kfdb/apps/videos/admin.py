from django.contrib import admin

from .models import Video


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    ordering = ("-release_date",)
    list_filter = (
        "show",
        "channel",
        "hosts",
        "producer",
        "short",
        "members_only",
    )

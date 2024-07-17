from django.contrib import admin, messages

from .models import Video
from apps.channels.models import Channel


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    ordering = ("-release_date",)
    list_filter = (
        "show",
        "channel",
        "hosts",
        "producer",
    )
    search_fields = ("title",)
    actions = ("channel_prime", "channel_games", "channel_members")

    @admin.action(description="Set Channel - KF Prime")
    def channel_prime(modeladmin, request, queryset):  # pragma: no cover
        channel = Channel.objects.only("pk").get(slug="prime")
        queryset.update(channel=channel)
        messages.success(request, "Successfully changed to KF Prime!")

    @admin.action(description="Set Channel - KF Games")
    def channel_games(modeladmin, request, queryset):  # pragma: no cover
        channel = Channel.objects.only("pk").get(slug="games")
        queryset.update(channel=channel)
        messages.success(request, "Successfully changed to KF Games!")

    @admin.action(description="Set Channel - KF Membership")
    def channel_members(modeladmin, request, queryset):  # pragma: no cover
        channel = Channel.objects.only("pk").get(slug="members")
        queryset.update(channel=channel)
        messages.success(request, "Successfully changed to KF Membership!")

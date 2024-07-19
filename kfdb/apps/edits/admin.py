from django.contrib import admin
from .models import ChannelEdit, HostEdit, ShowEdit, VideoEdit


class BaseEditAdmin(admin.ModelAdmin):
    ordering = ("-created_at",)
    list_filter = (
        "topic",
        "username",
        "status",
    )
    list_display = (
        "status",
        "topic_or_empty",
        "truncated_description",
        "truncated_name_or_empty",
        "created_at",
    )
    search_fields = ("description", "username")
    empty_value_display = "-empty-"

    def truncated_description(self, obj):
        return obj.description[:37] + "..."

    def truncated_name_or_empty(self, obj):
        if not obj.username:
            return "-empty-"
        return obj.username[:37] + "..."

    def topic_or_empty(self, obj):
        if not obj.topic:
            return "-empty-"
        return obj.topic

    truncated_description.short_description = "Description"
    truncated_name_or_empty.short_description = "Username"
    topic_or_empty.short_description = "Topic"


@admin.register(ChannelEdit)
class ChannelEditAdmin(BaseEditAdmin):
    readonly_fields = ["channel"]


@admin.register(HostEdit)
class HostEditAdmin(BaseEditAdmin):
    readonly_fields = ["host"]


@admin.register(ShowEdit)
class ShowEditAdmin(BaseEditAdmin):
    readonly_fields = ["show"]


@admin.register(VideoEdit)
class VideoEditAdmin(BaseEditAdmin):
    readonly_fields = ["video"]

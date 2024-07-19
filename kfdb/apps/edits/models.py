from django.db import models

from apps.channels.models import Channel
from apps.hosts.models import Host
from apps.shows.models import Show
from apps.videos.models import Video

STATUS_OPTIONS = {
    "NEW": "New",
    "VWD": "Viewed",
    "WIP": "In Progress",
    "CPL": "Complete",
    "CNC": "Cancelled",
    "SPM": "Spam",
}


class BaseEdit(models.Model):
    topic = models.CharField(max_length=32, blank=True)
    description = models.TextField(max_length=1000)
    username = models.CharField(max_length=255, blank=True)
    status = models.CharField(
        max_length=32, choices=STATUS_OPTIONS, default="NEW"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class ChannelEdit(BaseEdit):
    channel = models.ForeignKey(
        Channel,
        on_delete=models.CASCADE,
        related_name="edits",
    )


class HostEdit(BaseEdit):
    host = models.ForeignKey(
        Host,
        on_delete=models.CASCADE,
        related_name="edits",
    )


class ShowEdit(BaseEdit):
    show = models.ForeignKey(
        Show,
        on_delete=models.CASCADE,
        related_name="edits",
    )


class VideoEdit(BaseEdit):
    video = models.ForeignKey(
        Video,
        on_delete=models.CASCADE,
        related_name="edits",
    )

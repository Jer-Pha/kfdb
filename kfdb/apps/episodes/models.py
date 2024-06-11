from django.db import models

from apps.channels.models import Channel
from apps.hosts.models import Host
from apps.shows.models import Show


class Episode(models.Model):
    title = models.CharField(
        max_length=255,
        blank=False,
    )
    release_date = models.DateField(
        null=True,
        blank=True,
    )
    show = models.ForeignKey(
        Show,
        on_delete=models.CASCADE,
        related_query_name="episode",
    )
    channel = models.ForeignKey(
        Channel,
        on_delete=models.CASCADE,
        related_query_name="episode",
    )
    hosts = models.ManyToManyField(
        Host,
        related_query_name="episode",
    )
    video_id = models.CharField(
        max_length=11,
        unique=True,
    )
    url = models.URLField(
        max_length=43,
        blank=True,
    )
    blurb = models.TextField(
        null=True,
        blank=True,
        verbose_name="Blurb",
        help_text="Optional description of the episode.",
    )
    members_only = models.BooleanField(
        default=False,
        help_text="The episode is only available for YouTube/Patreon members.",
    )

    class Meta:
        default_related_name = "episodes"

    def __str__(self):
        return self.title

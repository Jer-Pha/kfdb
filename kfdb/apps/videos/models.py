from autoslug import AutoSlugField

from django.db import models
from django.utils.text import slugify

from apps.channels.models import Channel
from apps.hosts.models import Host
from apps.shows.models import Show


class Video(models.Model):
    title = models.CharField(
        max_length=255,
        blank=False,
    )
    slug = AutoSlugField(unique=True)
    release_date = models.DateField(
        null=True,
        blank=True,
    )
    show = models.ForeignKey(
        Show,
        null=True,
        blank=False,
        on_delete=models.CASCADE,
        related_name="videos",
        related_query_name="video_show",
    )
    channel = models.ForeignKey(
        Channel,
        null=True,
        blank=False,
        on_delete=models.CASCADE,
        related_name="videos",
        related_query_name="video_channel",
    )
    hosts = models.ManyToManyField(
        Host,
        related_name="hosted_videos",
        related_query_name="video_host",
        limit_choices_to=models.Q(kf_crew=True) | models.Q(part_timer=True),
    )
    guests = models.ManyToManyField(
        Host,
        related_name="guest_in_videos",
        related_query_name="video_guest",
        limit_choices_to={
            "kf_crew": False,
            "part_timer": False,
        },
    )
    producer = models.ForeignKey(
        Host,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="produced_videos",
        related_query_name="video_producer",
        limit_choices_to={
            "kf_crew": True,
        },
    )
    video_id = models.CharField(
        max_length=11,
        unique=True,
    )
    link = models.URLField(
        max_length=43,
        blank=True,
    )
    blurb = models.TextField(
        null=True,
        blank=True,
        verbose_name="Blurb",
        help_text="Optional description of the video.",
    )
    short = models.BooleanField(
        default=False,
        verbose_name="YouTube Short",
    )
    members_only = models.BooleanField(
        default=False,
        help_text="The video is only available for YouTube/Patreon members.",
    )

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

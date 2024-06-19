from autoslug import AutoSlugField

from django.db import models
from django.utils.text import slugify

from apps.channels.models import Channel
from apps.hosts.models import Host
from apps.shows.models import Show

SHOWS_PRIME = [
    "Portillo",
    "Follow the Liter",
    "A Conversation With Colin",
    "Colin Was Right",
    "Vlog",
    "Kinda Anime",
    "The Spare Bedroom",
    "We Have Cool Friends",
    "Screencast",
    "Kinda Funny Podcast",
    "Debatable",
    "KF/AF",
    "Internet Explorerz",
    "In Review",
    "Kinda Funny Morning Show",
    "Animated",
    "Love & Sex Stuff",
    "Kinda Funny Live",
    "Nick Names",
    "The GameOverGreggy Show",
    "Cooking With Greggy",
    "Oreo Oration",
]

SHOWS_GAMES = [
    "Showcase",
    "Kinda Funny Football League",
    "First Impressions",
    "The PSVR Show",
    "Party Mode",
    "Game Showdown",
    "The Blessing Show",
    "Kinda Funny Wrestling",
    "Xcast",
    "Reactions",
    "PS I Love You XOXO",
    "Gameplay",
    "Kinda Funny Games Daily",
    "Gamescast",
]


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
        blank=True,
        related_name="hosted_videos",
        related_query_name="video_host",
        limit_choices_to=models.Q(kf_crew=True) | models.Q(part_timer=True),
    )
    guests = models.ManyToManyField(
        Host,
        blank=True,
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
        help_text="Video description",
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
        if not self.slug:
            self.slug = slugify(self.title)

        s = self.show
        c = self.channel

        if (
            s
            and s.name in SHOWS_PRIME
            and (c and c.name != "Kinda Funny" or not c)
        ):
            self.channel = Channel.objects.get(name="Kinda Funny")
        elif (
            s
            and s.name in SHOWS_GAMES
            and (c and c.name != "Kinda Funny Games" or not c)
        ):
            self.channel = Channel.objects.get(name="Kinda Funny Games")
        elif s and s.name == "Shorts" and not self.short:
            self.short = True
        elif s and s.name != "Shorts" and self.short:
            self.show = Show.objects.get(name="Shorts")

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

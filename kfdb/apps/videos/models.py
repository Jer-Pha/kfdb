from autoslug import AutoSlugField

from django.db import models
from django.utils.text import slugify

from apps.channels.models import Channel
from apps.hosts.models import Host
from apps.shows.models import Show


@models.CharField.register_lookup
@models.TextField.register_lookup
class MySqlSearch(models.Lookup):
    lookup_name = "search"

    def as_mysql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = lhs_params + rhs_params
        return "MATCH (%s) AGAINST (%s IN BOOLEAN MODE)" % (lhs, rhs), params


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
        max_length=200,
        blank=True,
    )
    blurb = models.TextField(
        blank=True,
        verbose_name="Blurb",
        help_text="Video description",
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    @property
    def embed_size(self):
        if "youtube" in self.link and "shorts" not in self.link:
            return "w-full aspect-[16/9]"
        elif "youtube" in self.link:
            return "w-[270px] aspect-[9/16]"
        return ""

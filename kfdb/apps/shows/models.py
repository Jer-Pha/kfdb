from django.db import models
from django.utils.text import slugify

from apps.channels.models import Channel


def slug_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/uploads/img/shows/<slug>/<filename>
    return f"uploads/img/shows/{instance.slug}/{filename}"


class Show(models.Model):
    name = models.CharField(
        max_length=255,
        blank=False,
        unique=True,
    )
    slug = models.SlugField(
        unique=True,
        db_index=False,
        help_text="URL-compatible show name.",
    )
    image = models.ImageField(
        upload_to=slug_directory_path,
        blank=True,
        help_text="640x640 webp",
    )
    image_xs = models.ImageField(
        upload_to=slug_directory_path,
        blank=True,
        help_text="128x128 webp",
    )
    active = models.BooleanField(
        default=False,
        verbose_name="Is Active",
        db_index=True,
    )
    blurb = models.TextField(
        blank=True,
        help_text="Optional description of the show.",
    )
    channels = models.ManyToManyField(
        Channel,
        blank=True,
        related_name="channel_shows",
        related_query_name="show_channel",
        help_text="Channels this show might appear on.",
    )

    class Meta:
        indexes = [
            models.Index(fields=["slug", "name"], name="show_slug_name_idx"),
        ]

    def save(self, *args, **kwargs):
        """Ensure new shows have a slug."""
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

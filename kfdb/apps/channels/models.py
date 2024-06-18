from django.db import models
from django.utils.text import slugify


class Channel(models.Model):
    name = models.CharField(
        max_length=255,
        blank=False,
        unique=True,
    )
    slug = models.SlugField(unique=True)
    blurb = models.TextField(
        null=True,
        blank=True,
        help_text="Optional description of the channel.",
    )

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

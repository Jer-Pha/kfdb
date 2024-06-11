from django.db import models


class Channel(models.Model):
    name = models.CharField(
        max_length=255,
        blank=False,
        unique=True,
    )
    blurb = models.TextField(
        null=True,
        blank=True,
        help_text="Optional description of the channel.",
    )

    def __str__(self):
        return self.name

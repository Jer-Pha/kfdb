from django.db import models


class Show(models.Model):
    name = models.CharField(
        max_length=255,
        blank=False,
        unique=True,
    )
    active = models.BooleanField(
        default=False,
        verbose_name="Is Active",
    )
    blurb = models.TextField(
        null=True,
        blank=True,
        help_text="Optional description of the show.",
    )

    def __str__(self):
        return self.name

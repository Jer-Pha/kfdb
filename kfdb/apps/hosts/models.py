from django.db import models


class Host(models.Model):
    name = models.CharField(
        max_length=255,
        blank=False,
        unique=True,
    )
    nicknames = models.JSONField(
        null=True,
        blank=True,
        verbose_name="Nickname(s)",
        help_text="Should be formatted as a list, not dict.",
    )
    kf_crew = models.BooleanField(
        default=False,
        verbose_name="Kinda Funny Employee",
    )
    part_timer = models.BooleanField(
        default=False,
    )
    socials = models.JSONField(
        null=True,
        blank=True,
        help_text="Should be formatted as a dict.",
    )
    birthday = models.DateField(
        null=True,
        blank=True,
    )
    blurb = models.TextField(
        null=True,
        blank=True,
        help_text="Optional description or interesting notes about the host.",
    )

    def __str__(self):
        return self.name

    @property
    def name_lower(self):
        return self.name.lower()

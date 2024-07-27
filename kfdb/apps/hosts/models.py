from datetime import datetime
from random import choice

from django.core.cache import cache
from django.db import models
from django.db.models import Count, F
from django.utils.functional import cached_property
from django.utils.text import slugify


def slug_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/uploads/img/hosts/<slug>/<filename>
    return f"uploads/img/hosts/{instance.slug}/{filename}"


class Host(models.Model):
    name = models.CharField(
        max_length=255,
        blank=False,
        unique=True,
    )
    slug = models.SlugField(
        unique=True,
        help_text="URL-compatible host name.",
    )
    nicknames = models.JSONField(
        null=True,
        blank=True,
        verbose_name="Nickname(s)",
        help_text="Should be formatted as a list.",
    )
    image = models.ImageField(
        upload_to=slug_directory_path,
        blank=True,
        help_text="640x640 webp",
    )
    image_xs = models.ImageField(
        upload_to=slug_directory_path,
        blank=True,
        help_text="96x96 webp",
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
        help_text="Should be formatted as a dictionary.",
    )
    birthday = models.DateField(
        null=True,
        blank=True,
    )
    blurb = models.TextField(
        blank=True,
        help_text="Optional description or interesting notes about the host.",
    )

    class Meta:
        ordering = ("-kf_crew", "-part_timer", "name")
        indexes = [
            models.Index(fields=["kf_crew", "part_timer"], name="crew_pt_idx"),
        ]

    def save(self, *args, **kwargs):
        """Ensure new hosts have a slug."""
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @cached_property
    def url_type(self):
        """Used in template when creating link to host's page."""
        url = cache.get(f"url_type_{self.slug}")
        if not url:
            if self.kf_crew:
                url = "kf-crew"
            elif self.part_timer:
                url = "part-timers"
            else:
                url = "guests"
            cache.set(
                f"url_type_{self.slug}",
                url,
                60 * 15,  # 15 minutes
            )
        return url

    @cached_property
    def initials(self):
        """Used in template when host does not have an image."""
        initial = cache.get(f"initials_{self.slug}")
        if not initial:
            if self.slug == "fran-mirabella-iii":
                initial = "FM3"
            elif self.slug[-3:] == "-jr":
                initial = "".join(
                    i[0].upper() for i in self.slug[:-3].split("-")
                )
            else:
                initial = "".join(i[0].upper() for i in self.slug.split("-"))
            cache.set(
                f"initials_{self.slug}",
                initial,
                60 * 15,  # 15 minutes
            )
        return initial

    @cached_property
    def border_color(self):
        """
        Used in template as ``image`` or ``image_xs`` border color.

        Does not apply to "producer" images.
        """
        color = cache.get(f"border_color_{self.slug}")
        if not color:
            if self.kf_crew:
                color = "primary"
            elif self.part_timer:
                color = "secondary"
            else:
                color = "accent"
            cache.set(
                f"border_color_{self.slug}",
                color,
                60 * 15,  # 15 minutes
            )
        return color

    @property
    def nickname(self):
        """Get a random nickname to display on the host's page."""
        if not self.nicknames:
            return ""
        elif self.slug == "joey":
            nickname = choice(self.nicknames)
            if nickname == "Christmas in >>Current Month<<":
                nickname = f"Christmas in {datetime.now().strftime('%B')}"
            return nickname
        return choice(self.nicknames)

    @cached_property
    def birth_day(self):
        """Birthday with the year removed for the host's page."""
        birthday = cache.get(f"birthday_{self.slug}")
        if not birthday:
            birthday = self.birthday.strftime("%B %d")
            cache.set(
                f"birthday_{self.slug}",
                birthday,
                60 * 15,  # 15 minutes
            )
        return birthday

    @cached_property
    def appearance_count(self):
        """Count of episodes hosted, produced, and total appearances."""
        appearances = cache.get(f"appearance_count_{self.slug}")
        if not appearances:
            appearances = (
                Host.objects.filter(id=self.id)
                .annotate(
                    hosted=Count("video_host", distinct=True),
                    produced=Count("video_producer", distinct=True),
                    appearances=(F("hosted") + F("produced")),
                )
                .values("appearances")
                .first()
            )["appearances"]
            cache.set(
                f"appearance_count_{self.slug}",
                appearances,
                60 * 15,  # 15 minutes
            )
        return appearances

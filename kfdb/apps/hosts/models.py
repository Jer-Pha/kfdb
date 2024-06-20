from django.db import models
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
    slug = models.SlugField(unique=True)
    nicknames = models.JSONField(
        null=True,
        blank=True,
        verbose_name="Nickname(s)",
        help_text="Should be formatted as a list, not dict.",
    )
    image = models.ImageField(upload_to=slug_directory_path, blank=True)
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

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ("-kf_crew", "-part_timer", "name")

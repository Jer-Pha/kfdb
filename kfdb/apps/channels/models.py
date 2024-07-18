from django.db import models
from django.utils.text import slugify


def slug_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/uploads/img/channels/<slug>/<filename>
    return f"uploads/img/channels/{instance.slug}/{filename}"


class Channel(models.Model):
    name = models.CharField(
        max_length=255,
        blank=False,
        unique=True,
    )
    slug = models.SlugField(
        unique=True,
        help_text="URL-compatible channel name.",
    )
    image = models.ImageField(upload_to=slug_directory_path, blank=True)
    blurb = models.TextField(
        blank=True,
        help_text="Optional description of the channel.",
    )

    def save(self, *args, **kwargs):
        """Ensure new channels have a slug."""
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

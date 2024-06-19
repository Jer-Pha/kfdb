from django.db import models
from django.utils.text import slugify


class Show(models.Model):
    name = models.CharField(
        max_length=255,
        blank=False,
        unique=True,
    )
    slug = models.SlugField(unique=True)
    active = models.BooleanField(
        default=False,
        verbose_name="Is Active",
    )
    blurb = models.TextField(
        null=True,
        blank=True,
        help_text="Optional description of the show.",
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

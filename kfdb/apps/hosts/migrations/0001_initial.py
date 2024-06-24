# Generated by Django 5.0.6 on 2024-06-24 06:51

import apps.hosts.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Host",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255, unique=True)),
                ("slug", models.SlugField(unique=True)),
                (
                    "nicknames",
                    models.JSONField(
                        blank=True,
                        help_text="Should be formatted as a list, not dict.",
                        null=True,
                        verbose_name="Nickname(s)",
                    ),
                ),
                (
                    "image",
                    models.ImageField(
                        blank=True,
                        upload_to=apps.hosts.models.slug_directory_path,
                    ),
                ),
                (
                    "kf_crew",
                    models.BooleanField(
                        default=False, verbose_name="Kinda Funny Employee"
                    ),
                ),
                ("part_timer", models.BooleanField(default=False)),
                (
                    "socials",
                    models.JSONField(
                        blank=True,
                        help_text="Should be formatted as a dict.",
                        null=True,
                    ),
                ),
                ("birthday", models.DateField(blank=True, null=True)),
                (
                    "blurb",
                    models.TextField(
                        blank=True,
                        help_text="Optional description or interesting notes about the host.",
                    ),
                ),
            ],
            options={
                "ordering": ("-kf_crew", "-part_timer", "name"),
            },
        ),
    ]

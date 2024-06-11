# Generated by Django 5.0.6 on 2024-06-11 07:04

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
                        null=True,
                    ),
                ),
            ],
        ),
    ]

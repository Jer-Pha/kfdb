# Generated by Django 5.0.6 on 2024-06-26 06:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("videos", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="video",
            name="audio_only",
        ),
        migrations.RemoveField(
            model_name="video",
            name="guests",
        ),
    ]

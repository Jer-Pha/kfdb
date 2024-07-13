# Generated by Django 5.0.6 on 2024-07-13 07:29

import apps.channels.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("channels", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="channel",
            name="image",
            field=models.ImageField(
                blank=True, upload_to=apps.channels.models.slug_directory_path
            ),
        ),
    ]

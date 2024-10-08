# Generated by Django 5.0.6 on 2024-07-18 00:14

import apps.shows.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("channels", "0003_alter_channel_blurb_alter_channel_name"),
        ("shows", "0005_alter_show_channels"),
    ]

    operations = [
        migrations.AlterField(
            model_name="show",
            name="channels",
            field=models.ManyToManyField(
                blank=True,
                help_text="Channels this show might appear on.",
                related_name="channel_shows",
                related_query_name="show_channel",
                to="channels.channel",
            ),
        ),
        migrations.AlterField(
            model_name="show",
            name="image",
            field=models.ImageField(
                blank=True,
                help_text="640x640 webp",
                upload_to=apps.shows.models.slug_directory_path,
            ),
        ),
        migrations.AlterField(
            model_name="show",
            name="image_xs",
            field=models.ImageField(
                blank=True,
                help_text="128x128 webp",
                upload_to=apps.shows.models.slug_directory_path,
            ),
        ),
        migrations.AlterField(
            model_name="show",
            name="slug",
            field=models.SlugField(
                db_index=False,
                help_text="URL-compatible show name.",
                unique=True,
            ),
        ),
    ]

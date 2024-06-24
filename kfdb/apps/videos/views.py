from django.shortcuts import render
from django.views.decorators.http import require_GET

from .models import Video


@require_GET
def get_video_details(request):
    video_id = request.GET.get("video_id", "")

    video = (
        Video.objects.select_related("show", "producer")
        .defer("title")
        .prefetch_related("hosts", "guests")
        .get(video_id=video_id)
    )

    context = {
        "video": video,
    }

    return render(request, "videos/partials/get-video-details.html", context)


# Temporary
def upload_view(request):  # pragma: no cover
    """This is a temporary view to load existing data into the db."""

    from csv import reader
    from datetime import datetime
    from os import path

    from django.conf import settings
    from django.http import HttpResponse

    from apps.channels.models import Channel
    from apps.hosts.models import Host
    from apps.shows.models import Show
    from apps.videos.models import Video

    i = 0
    file_path = path.join(
        settings.BASE_DIR / "resources", "import_channels.csv"
    )
    with open(file_path, "r", encoding="utf-8") as file:
        data = reader(file)
        batch = []
        for row in data:
            channel = Channel(name=row[0], slug=row[1])
            batch.append(channel)
            i += 1
        Channel.objects.bulk_create(batch)
        print(f"{i} / 3 channels created")

    i = 0
    file_path = path.join(settings.BASE_DIR / "resources", "import_hosts.csv")
    with open(file_path, "r", encoding="utf-8") as file:
        data = reader(file)
        batch = []
        for row in data:
            host = Host(
                name=row[0],
                slug=row[1],
                kf_crew=row[2] == "True",
                part_timer=row[3] == "True",
            )
            batch.append(host)
            i += 1
        Host.objects.bulk_create(batch)
        print(f"{i} / 830 hosts created")

    i = 0
    file_path = path.join(settings.BASE_DIR / "resources", "import_shows.csv")
    with open(file_path, "r", encoding="utf-8") as file:
        data = reader(file)
        batch = []
        for row in data:
            host = Show(
                name=row[0],
                slug=row[1],
                active=row[2] == "True",
            )
            batch.append(host)
            i += 1
        Show.objects.bulk_create(batch)
        print(f"{i} / 49 shows created")

    i = 0
    file_path = path.join(settings.BASE_DIR / "resources", "import_videos.csv")

    with open(file_path, "r", encoding="utf-8") as file:
        data = reader(file)
        for row in data:
            video = Video.objects.create(
                title=row[0],
                slug=row[1],
                release_date=datetime.fromisoformat(row[2]),
                show=Show.objects.get(name=row[3]),
                channel=Channel.objects.get(name=row[4]),
                video_id=row[5],
                link=row[6],
                blurb=row[7],
            )

            host_batch = []

            for name in (n for n in row[8].split(",") if n):
                host_batch.append(Host.objects.get(name=name))

            video.hosts.add(*host_batch)
            i += 1
        print(f"{i} / 10057 shows created")

    return HttpResponse("Done")

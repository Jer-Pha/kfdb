from re import sub

from django.conf import settings
from django.core.paginator import Paginator
from django.db import connection
from django.db.models import Q
from django.shortcuts import render
from django.views.decorators.http import require_GET

from .models import Video
from apps.channels.models import Channel
from apps.hosts.models import Host
from apps.shows.models import Show


@require_GET
def videos_home(request):
    page = int(request.GET.get("page", 1))
    sort = request.GET.get("sort", "-release_date")
    search = sub(" +", " ", request.GET.get("search", "").strip())
    filter_channel = request.GET.get("channel", "")
    filter_show = request.GET.get("show", "")
    filter_guest = request.GET.get("guest", "")
    filter_producer = request.GET.get("producer", "")
    filter_part_timer = request.GET.get("part-timer", "")
    filter_crew = dict(request.GET).get("crew", [])
    results_per_page = request.GET.get("results", 25)

    videos = Video.objects.select_related("show")

    filter_params = {}

    if filter_channel:
        filter_params["channel__slug"] = filter_channel

    if filter_show:
        filter_params["show__slug"] = filter_show

    if filter_producer:
        filter_params["producer__slug"] = filter_producer

    if search and not settings.DEBUG:
        videos = videos.filter(
            Q(blurb__search=search) | Q(title__search=search)
        )
    elif search:
        videos = videos.filter(
            Q(blurb__icontains=search) | Q(title__icontains=search)
        )

    if filter_crew:
        if filter_guest:
            filter_crew.append(filter_guest)
        if filter_part_timer:
            filter_crew.append(filter_part_timer)

        for host in filter_crew:
            videos = videos.filter(hosts__slug=host)
    else:
        if filter_guest:
            videos = videos.filter(hosts__slug=filter_guest)
        if filter_part_timer:
            videos = videos.filter(hosts__slug=filter_part_timer)

    videos = (
        videos.filter(**filter_params)
        .only(
            "title",
            "video_id",
            "release_date",
            "show",
            "show__name",
            "show__image",
        )
        .order_by(sort)
    )

    paginator = Paginator(videos, results_per_page)
    page_count = paginator.num_pages
    videos = paginator.get_page(page).object_list

    context = {
        "videos": videos,
    }

    # Standard page load
    if "Hx-Boosted" in request.headers or not "Hx-Request" in request.headers:

        context.update(
            {
                "curr_path": request.path,
            }
        )

        return render(request, "videos/videos-home.html", context)

    return render(request, "videos/partials/get-video-results.html", context)


@require_GET
def get_video_details(request):
    video_id = request.GET.get("video_id", "")

    video = (
        Video.objects.select_related("show", "producer", "channel")
        .prefetch_related("hosts")
        .get(video_id=video_id)
    )

    context = {
        "video": video,
    }

    return render(request, "videos/partials/get-video-details.html", context)


# Temporary
def upload_view(request):  # pragma: no cover
    """This is a temporary view to load existing data into the db."""

    # from csv import reader
    # from datetime import datetime
    # from os import path

    # from django.conf import settings
    from django.http import HttpResponse

    # from apps.channels.models import Channel
    # from apps.hosts.models import Host
    # from apps.shows.models import Show
    # from apps.videos.models import Video

    # i = 0
    # file_path = path.join(
    #     settings.BASE_DIR / "resources", "import_channels.csv"
    # )
    # with open(file_path, "r", encoding="utf-8") as file:
    #     data = reader(file)
    #     batch = []
    #     for row in data:
    #         channel = Channel(name=row[0], slug=row[1])
    #         batch.append(channel)
    #         i += 1
    #     Channel.objects.bulk_create(batch)
    #     print(f"{i} / 3 channels created")

    # i = 0
    # file_path = path.join(settings.BASE_DIR / "resources", "import_hosts.csv")
    # with open(file_path, "r", encoding="utf-8") as file:
    #     data = reader(file)
    #     batch = []
    #     for row in data:
    #         host = Host(
    #             name=row[0],
    #             slug=row[1],
    #             kf_crew=row[2] == "True",
    #             part_timer=row[3] == "True",
    #         )
    #         batch.append(host)
    #         i += 1
    #     Host.objects.bulk_create(batch)
    #     print(f"{i} / 830 hosts created")

    # i = 0
    # file_path = path.join(settings.BASE_DIR / "resources", "import_shows.csv")
    # with open(file_path, "r", encoding="utf-8") as file:
    #     data = reader(file)
    #     batch = []
    #     for row in data:
    #         host = Show(
    #             name=row[0],
    #             slug=row[1],
    #             active=row[2] == "True",
    #         )
    #         batch.append(host)
    #         i += 1
    #     Show.objects.bulk_create(batch)
    #     print(f"{i} / 49 shows created")

    # try:
    #     i = 0
    #     file_path = path.join(
    #         settings.BASE_DIR / "resources", "import_videos.csv"
    #     )

    #     with open(file_path, "r", encoding="utf-8") as file:
    #         data = reader(file)
    #         for row in data:
    #             video = Video.objects.create(
    #                 title=row[0],
    #                 slug=row[1],
    #                 release_date=datetime.fromisoformat(row[2]),
    #                 show=Show.objects.get(name=row[3]),
    #                 channel=Channel.objects.get(name=row[4]),
    #                 video_id=row[5],
    #                 link=row[6],
    #                 blurb=row[7],
    #             )

    #             host_batch = []

    #             for name in (n for n in row[8].split(",") if n):
    #                 host_batch.append(Host.objects.get(name=name))

    #             video.hosts.add(*host_batch)
    #             i += 1
    #         print(f"{i} / 10057 shows created")
    # except Exception as e:
    #     print(e)

    return HttpResponse("Done")

from re import sub

from django.conf import settings
from django.core.paginator import Paginator
from django.db import connection
from django.db.models import Q
from django.shortcuts import render
from django.views.decorators.http import require_GET

from .models import Show
from apps.videos.models import Video


@require_GET
def show_page(request, show):
    page = int(request.GET.get("page", 1))
    sort = request.GET.get("sort", "-release_date")
    search = sub(" +", " ", request.GET.get("search", "").strip())
    filter_channel = request.GET.get("channel", "")
    filter_guest = request.GET.get("guest", "")
    filter_producer = request.GET.get("producer", "")
    filter_part_timer = request.GET.get("part-timer", "")
    filter_crew = dict(request.GET).get("crew", [])
    results_per_page = request.GET.get("results", 25)

    show = Show.objects.values("id", "name", "blurb").get(slug=show)
    videos = Video.objects.select_related("show")
    filter_params = {"show": show["id"]}

    if filter_channel:
        filter_params["channel__slug"] = filter_channel

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
            "channel",
        )
        .order_by(sort)
    )

    paginator = Paginator(videos, results_per_page)
    page_count = paginator.num_pages
    videos = paginator.get_page(page).object_list

    context = {
        "videos": videos,
    }

    for query in connection.queries:
        print(query)

    # Standard page load
    if "Hx-Boosted" in request.headers or not "Hx-Request" in request.headers:

        context.update(
            {
                "show": show,
                "curr_path": request.path,
            }
        )

        return render(request, "shows/show-page.html", context)

    return render(request, "videos/partials/get-video-results.html", context)

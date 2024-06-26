from django.conf import settings
from django.core.paginator import Paginator
from django.db import connection
from django.shortcuts import render
from django.views.decorators.http import require_GET

from .models import Channel
from apps.videos.models import Video


def channels_home(request):
    context = {}

    return render(request, "channels/channels-home.html", context)


@require_GET
def channel_page(request, channel):
    # paginator = Paginator(qs, results_per_page)
    # page_count = paginator.num_pages
    # page = request.GET.get("page", 1)

    sort = request.GET.get("sort", "-release_date")
    search = request.GET.get("search", "")
    filter_show = request.GET.get("show", "")
    filter_host = request.GET.get("host", "")
    filter_crew = dict(request.GET).get("crew", [])
    results_per_page = request.GET.get("results", 25)

    channel = Channel.objects.values().get(slug=channel)

    filter_params = {
        "channel": channel["id"],
    }

    if search and not settings.DEBUG:
        filter_params["blurb__search"] = search
        filter_params["title__search"] = search
    elif search:
        filter_params["blurb__icontains"] = search
        filter_params["title__icontains"] = search

    if filter_show:
        filter_params["show__slug"] = filter_show

    if filter_crew and filter_host:
        filter_crew.append(filter_host)
        filter_params["hosts__slug__in"] = filter_crew
    elif filter_crew:
        filter_params["hosts__slug__in"] = filter_crew
    elif filter_host:
        filter_params["hosts__slug"] = filter_host

    videos = (
        Video.objects.select_related("show")
        .only(
            "title",
            "video_id",
            "release_date",
            "show",
            "show__name",
            "show__image",
        )
        .filter(**filter_params)
        .order_by(sort)[:results_per_page]
    )

    print(filter_params)

    context = {
        "videos": videos,
    }

    # Standard page load
    if "Hx-Boosted" in request.headers or not "Hx-Request" in request.headers:

        context.update(
            {
                "channel": channel,
                "curr_path": request.path,
            }
        )

        return render(request, "channels/channel-page.html", context)

    return render(request, "videos/partials/get-video-results.html", context)

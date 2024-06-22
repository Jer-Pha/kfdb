from django.core.paginator import Paginator
from django.shortcuts import render
from django.views.decorators.http import require_GET

from .models import Channel
from apps.videos.models import Video


def channels_home(request):
    context = {}

    return render(request, "channels/channels-home.html", context)


@require_GET
def channel_page(request, channel):
    page = request.GET.get("page", 1)
    search = request.GET.get("search", "")
    filter_crew = request.GET.get("crew", "").split(",")
    filter_part_timers = request.GET.get("part-timers", "").split(",")
    filter_guests = request.GET.get("guests", "").split(",")
    filter_show = request.GET.get("shows", "").split(",")
    results_per_page = request.GET.get("per_page", 25)

    channel = Channel.objects.values().get(slug=channel)

    build_filter = {
        "shows_active": list(
            Video.objects.select_related("show")
            .filter(channel=channel["id"], show__active=True)
            .distinct()
            .values_list("show__slug", "show__name")
            .order_by("show__name")
        ),
        "shows_inactive": list(
            Video.objects.select_related("show")
            .filter(channel=channel["id"], show__active=False)
            .distinct()
            .values_list("show__slug", "show__name")
            .order_by("show__name")
        ),
    }

    # Standard page load
    if not "HX-Request" in request.META:
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
            .filter(channel=channel["id"])
            .order_by("-release_date")[:results_per_page]
        )

        context = {
            "channel": channel,
            "videos": videos,
            "build_filter": build_filter,
        }

        return render(request, "channels/channel-page.html", context)

    # HTMX request for pagination
    paginator = Paginator(qs, results_per_page)
    page_count = paginator.num_pages

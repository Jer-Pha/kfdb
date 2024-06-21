from django.http import HttpResponse
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
    host_filter = request.GET.get("hosts", "").split(",")
    guest_filter = request.GET.get("guest", "").split(",")
    show_filter = request.GET.get("shows", "").split(",")

    # Standard page load
    if not "HX-Request" in request.META:
        channel = Channel.objects.values().get(slug=channel)
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
            .order_by("-release_date")[:10]
        )

        print(channel)

        context = {
            "channel": channel,
            "videos": videos,
        }

        return render(request, "channels/channel-page.html", context)

    # HTMX request for pagination

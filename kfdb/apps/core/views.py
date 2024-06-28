from urllib.parse import urlencode

from django.conf import settings
from django.db.models import Count, Q
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET

from apps.channels.models import Channel
from apps.core.utils import Filter
from apps.hosts.models import Host
from apps.videos.models import Video


@require_GET
def homepage(request):
    context = {}

    return render(request, "core/index.html", context)


@require_GET
def update_index_stats(request):
    count = Host.objects.only("pk", "kf_crew", "part_timer").aggregate(
        crew=Count("pk", filter=Q(kf_crew=True, part_timer=False)),
        pt=Count("pk", filter=Q(kf_crew=False, part_timer=True)),
        guest=Count("pk", filter=Q(kf_crew=False, part_timer=False)),
    )
    count["video"] = Video.objects.all().count()

    context = {
        "count": count,
    }

    return render(request, "core/partials/update-index-stats.html", context)


@require_GET
def build_filter(request):
    if "c" in request.GET:
        context = Filter(
            channel_id=int(request.GET.get("c", 0))
        ).channel_filter()
    elif "s" in request.GET:
        context = Filter(show_id=int(request.GET.get("s", 0))).show_filter()
    elif "h" in request.GET:
        context = Filter(host_id=int(request.GET.get("h", 0))).host_filter()
    else:
        context = Filter().host_filter()

    context["curr_path"] = request.GET.get("u", "")

    return render(request, "core/partials/build-filter.html", context)


@require_GET
def update_theme(request):
    if "theme" not in request.GET:
        return HttpResponse(status=404)

    theme = request.GET["theme"]
    theme_cookie = request.get_signed_cookie(
        key="kfdb_theme",
        salt=settings.KFDB_COOKIE_SALT,
        max_age=31536000,
        default=None,
    )

    if not theme_cookie or theme != theme_cookie:
        response = HttpResponse(status=200)
        response.set_signed_cookie(
            key="kfdb_theme",
            value=theme,
            salt=settings.KFDB_COOKIE_SALT,
            max_age=31536000,
            secure=False,
            httponly=True,
            samesite="Lax",
        )

        return response
    else:
        return HttpResponse(status=304)

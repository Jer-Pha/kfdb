from urllib.parse import urlencode

from django.conf import settings
from django.db.models import Count, Q
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET

from apps.hosts.models import Host
from apps.videos.models import Video


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
            secure=True,
            httponly=True,
            samesite="Lax",
        )

        return response
    else:
        return HttpResponse(status=304)

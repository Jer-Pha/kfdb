from django.db.models import Count, Q
from django.http import HttpResponse
from django.views.decorators.http import require_GET

from apps.hosts.models import Host
from apps.videos.models import Video


@require_GET
def update_index_stats(request):
    c = Host.objects.only("pk", "kf_crew", "part_timer").aggregate(
        crew=Count("pk", filter=Q(kf_crew=True, part_timer=False)),
        pt=Count("pk", filter=Q(kf_crew=False, part_timer=True)),
        guest=Count("pk", filter=Q(kf_crew=False, part_timer=False)),
    )
    video_count = Video.objects.all().count()

    return HttpResponse(
        f"<span>{c['crew']}</span>"
        f'<span hx-swap-oob="#part-timer-count">{c['pt']}</span>'
        f'<span hx-swap-oob="#guest-count">{c['guest']}</span>'
        f'<span hx-swap-oob="#video-count">{video_count}</span>'
    )

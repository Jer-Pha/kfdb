from django.db.models import Q

from apps.videos.models import Video


def global_context(request):
    games_active = (
        Video.objects.select_related("channel", "show")
        .only(
            "channel",
            "channel__slug",
            "show",
            "show__active",
            "show__name",
            "show__slug",
        )
        .filter(channel__slug="kfg", show__active=True)
        .values("show__name", "show__slug")
        .distinct()
    )
    prime_active = (
        Video.objects.select_related("channel", "show")
        .only(
            "channel",
            "channel__slug",
            "show",
            "show__active",
            "show__name",
            "show__slug",
        )
        .filter(channel__slug="kf", show__active=True)
        .values("show__name", "show__slug")
        .distinct()
    )

    return {
        "games_active": games_active,
        "prime_active": prime_active,
    }

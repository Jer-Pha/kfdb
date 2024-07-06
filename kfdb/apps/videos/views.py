from apps.core.views import DefaultVideoView


class ChannelPageView(DefaultVideoView):
    template_name = ""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.template_name = (
            "videos/videos-home.html"
            if self.new_page
            else "core/partials/get-video-results.html"
        )
        filter_params = {}
        context["videos"] = self.get_videos(filter_params)

        return context


def upload_view(request):
    from datetime import datetime
    from feedparser import parse

    from django.conf import settings
    from django.http import HttpResponse
    from django.db.models import Q
    from django.template.defaultfilters import slugify
    from django.utils.crypto import get_random_string

    from .models import Video
    from apps.channels.models import Channel
    from apps.shows.models import Show

    posts = parse(settings.PATREON_RSS_FEED)["entries"]

    Video.objects.filter(
        Q(title__icontains="review & reactions")
        | Q(title__icontains="review and reactions")
    ).filter(
        show=Show.objects.get(slug="reactions"),
        channel=Channel.objects.get(slug="games"),
    ).update(
        show=Show.objects.get(slug="screencast"),
        channel=Channel.objects.get(slug="prime"),
    )

    for post in posts:
        video_id = post["id"]
        title = post["title"]
        slug = slugify(title)[:51]

        if Video.objects.filter(video_id=video_id).exists():
            continue
        elif Video.objects.filter(slug=slug).exists():
            slug = f"{slug}-{get_random_string(length=1)}"

        show_slug = ""
        title_lower = title.lower()

        if "gregway" in title_lower:
            show_slug = "gregway"
        elif (
            "sh!t list" in title_lower
            or "shi!t list" in title_lower
            or "shit list" in title_lower
        ):
            show_slug = "sht-list"
        elif "kinda funny podcast" in title_lower:
            show_slug = "kf-podcast"
        elif "game showdown" in title_lower:
            show_slug = "game-showdown"
        elif "kinda feudy" in title_lower:
            show_slug = "kinda-feudy"
        elif "gamescast" in title_lower:
            show_slug = "gamescast"
        elif "we have cool friends" in title_lower:
            show_slug = "we-have-cool-friends"
        elif "kinda funny games daily" in title_lower:
            show_slug = "kfgd"
        elif (
            "in review" in title_lower
            or "ranked & recapped" in title_lower
            or "reviewed & ranked" in title_lower
            or "reviewed and ranked" in title_lower
            or "ranked & reviewed" in title_lower
            or "ranked, reviewed, & recapped " in title_lower
            or "ranked, reviewed, and recapped " in title_lower
        ):
            show_slug = "in-review"
        elif "xcast" in title_lower:
            show_slug = "xcast"
        elif "ps i love you" in title_lower:
            show_slug = "psily"
        elif (
            "kinda funny next-gen" in title_lower
            or "kinda funny next gen" in title_lower
        ):
            show_slug = "next-gen"
        elif "remember" in title_lower:
            show_slug = "remember-blank"
        elif "gameovergreggy" in title_lower or "gog" in title_lower:
            show_slug = "gog"
        elif "comic book club" in title_lower:
            show_slug = "comic-book-club"
        elif "debatable" in title_lower:
            show_slug = "debatable"
        elif (
            "screencast" in title_lower
            or "wrestlemania ranked" in title_lower
            or "review & reactions" in title_lower
            or "finale review" in title_lower
            or "movie review" in title_lower
            or (
                "episode" in title_lower
                and ("review" in title_lower or "breakdown" in title_lower)
            )
            or (
                "season" in title_lower
                and ("review" in title_lower or "breakdown" in title_lower)
            )
        ):
            show_slug = "screencast"
        elif "explorerz" in title_lower:
            show_slug = "internet-explorerz"
        elif "kf/af" in title_lower or "kfaf" in title_lower:
            show_slug = "kfaf"
        elif "kinda anime" in title_lower:
            show_slug = "kinda-anime"
        elif "reaction" in title_lower:
            show_slug = "reactions"
        elif (
            "ama" in title_lower
            or "ask kf anything" in title_lower
            or "q&a" in title_lower
            or "intimate in title_lower" in title_lower
        ):
            show_slug = "ama"

        Video.objects.create(
            video_id=post["id"],
            title=title,
            slug=slug,
            link=post["link"],
            release_date=datetime.strptime(
                " ".join(str(post["published"]).split(" ")[1:4]), "%d %b %Y"
            ),
            channel=Channel.objects.get(slug="members"),
            show=None if not show_slug else Show.objects.get(slug=show_slug),
        )

    return HttpResponse(status=200)

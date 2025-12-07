from collections import OrderedDict
from datetime import date, datetime, timedelta

from apps.channels.models import Channel
from apps.core.views import DefaultVideoView
from apps.shows.models import Show
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.db.models import Count, Q
from django.db.models.functions import TruncMonth
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import cache_page
from django.views.generic import TemplateView
from feedparser import parse
from requests import get, head

from .models import Video


class AllVideosView(DefaultVideoView):
    template_name = ""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.template_name = (
            "videos/videos-home.html"
            if self.new_page
            else "videos/partials/get-video-results.html"
        )
        filter_params = {}
        videos = cache.get(self.request.build_absolute_uri())

        if not videos:
            videos = self.get_videos(filter_params)
            cache.set(
                self.request.build_absolute_uri(),
                videos,
                60 * 5,  # 5 minutes
            )
        context["videos"] = videos

        return context


@method_decorator(
    cache_page(60 * 5, key_prefix="video_details"),
    name="dispatch",
)
class VideoDetailsView(TemplateView):
    http_method_names = "get"
    template_name = "videos/partials/get-video-details.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        video = (
            Video.objects.select_related("show", "producer", "channel")
            .prefetch_related("hosts")
            .get(video_id=self.request.GET.get("video_id", ""))
        )
        context["video"] = video
        return context


class VideoBlurbView(TemplateView):
    http_method_names = "get"
    template_name = "videos/partials/get-video-blurb.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        blurb = Video.objects.values_list("blurb", flat=True).get(
            video_id=self.request.GET.get("video_id", "")
        )
        context["blurb"] = blurb
        return context


class VideoEmbedView(TemplateView):
    http_method_names = "get"
    template_name = "videos/partials/get-video-embed.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        video = Video.objects.only("link", "title", "video_id").get(
            video_id=self.request.GET.get("video_id", "")
        )
        context["video"] = video
        return context


class UpdateVideosView(LoginRequiredMixin, View):  # pragma: no cover
    raise_exception = True

    def create_video(
        self,
        video_id,
        title,
        release_date,
        link,
        blurb,
        patreon=False,
        short=False,
        highlights=False,
    ):
        if Video.objects.filter(video_id=video_id).exists():
            return

        show_slug = ""
        channel_slug = ""
        title_lower = title.lower()

        if short:
            show_slug = "shorts"
        elif highlights:
            show_slug = "highlights"
        elif "gregway" in title_lower:
            show_slug = "gregway"
        elif "game showdown" in title_lower:
            show_slug = "game-showdown"
            channel_slug = "games"
        elif "gamescast" in title_lower:
            show_slug = "gamescast"
            channel_slug = "games"
        elif "kinda funny games daily" in title_lower:
            show_slug = "kfgd"
            channel_slug = "games"
        elif "kinda funny podcast" in title_lower:
            show_slug = "kf-podcast"
            channel_slug = "prime"
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
            channel_slug = "prime"
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
            channel_slug = "prime"
        elif "reaction" in title_lower:
            show_slug = "reactions"

        if patreon:
            release_date = datetime.strptime(
                " ".join(str(release_date).split(" ")[1:4]),
                "%d %b %Y",
            )
            channel_slug = "members"

        Video.objects.create(
            video_id=video_id,
            title=title,
            release_date=release_date,
            link=link,
            blurb=blurb,
            channel=(
                None
                if not channel_slug
                else Channel.objects.get(slug=channel_slug)
            ),
            show=None if not show_slug else Show.objects.get(slug=show_slug),
        )
        self.new_video_ids.append(video_id)

    def update_patreon(self):
        RSS_FEED = settings.PATREON_RSS_FEED
        posts = parse(RSS_FEED)["entries"]

        for post in posts:
            self.create_video(
                video_id=post["id"],
                title=post["title"],
                release_date=post["published"],
                link=post["link"],
                blurb="",
                patreon=True,
            )

    def update_youtube(self, channel, page, highlights=False):
        API_KEY = settings.YOUTUBE_API_KEY
        now = datetime.now().strftime("%H:%M:%S")
        today = date.today()
        delta = timedelta(days=30)
        published_before = f"{today + delta}T{now}Z"
        published_after = f"{today - delta}T{now}Z"
        max_results = 50
        channel_api_url = (
            f"https://youtube.googleapis.com/youtube/v3/search?key="
            f"{API_KEY}&channelId={channel}&part=snippet&maxResults="
            f"{max_results}&pageToken={page}&order=date&type=video&"
            f"publishedBefore={published_before}&publishedAfter="
            f"{published_after}"
        )
        response = get(url=channel_api_url).json()
        videos = response["items"]

        for video in videos:
            video_id = video["id"]["videoId"]
            title = video["snippet"]["title"]

            if (
                Video.objects.filter(video_id=video_id).exists()
                or title == "Private video"
                or title == "Deleted video"
            ):
                continue

            video_api_url = (
                "https://youtube.googleapis.com/youtube/v3/videos?part="
                f"contentDetails%2Csnippet&id={video_id}&key={API_KEY}"
            )
            vid = get(url=video_api_url).json()["items"][0]

            blurb = vid["snippet"]["description"]
            release_date = datetime.fromisoformat(
                vid["snippet"]["publishedAt"]
            ).date()

            video_url = f"https://www.youtube.com/shorts/{video_id}"
            short = True
            response = head(video_url, allow_redirects=False)

            if response.status_code != 200:
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                short = False

            self.create_video(
                video_id=video_id,
                title=title,
                release_date=release_date,
                link=video_url,
                blurb=blurb,
                short=short,
                highlights=highlights,
            )

        if "nextPageToken" in response:
            self.update_youtube(channel, response["nextPageToken"])

    def get(self, request, *args, **kwargs):
        try:
            self.new_video_ids = []
            self.update_youtube("UCT6QFE3peNry9PdO5uGj96g", "")  # Core
            self.update_youtube(
                "UCb4G6Wao_DeFr1dm8-a9zjg", "", highlights=True
            )  # Highlights
            self.update_patreon()  # Patreon
        except Exception as e:
            return HttpResponse(str(e), content_type="text/plain", status=500)

        return HttpResponse(
            f"New Videos: {','.join(self.new_video_ids)}",
            content_type="text/plain",
            status=200,
        )


@method_decorator(
    cache_page(60 * 5, key_prefix="host_chart_data"),
    name="dispatch",
)
class AllVideosChartsView(TemplateView):
    http_method_names = "get"
    template_name = "core/partials/get-charts.html"

    def get_show_count(self):
        """Calculates videos per show."""
        shows = list(
            Show.objects.all()
            .annotate(count=Count("video_show", distinct=True))
            .values("name", "count")
            .order_by("-count")
            .distinct()
        )

        data = {}
        other = 0

        for show in shows:
            if len(data) < 10:
                data[show["name"]] = show["count"]
            else:
                other += show["count"]

        data["Other"] = other

        context = {
            "doughnut_data": {
                "labels": list(data.keys()),
                "datasets": [
                    {
                        "label": " Shows",
                        "data": list(data.values()),
                        "borderWidth": 1,
                    },
                ],
            },
            "doughnut_fallback": list(data.items()),
            "doughnut_title": "Shows",
        }

        return context

    def get_monthly_count(self):
        """Calculates episodes per month for all videos."""
        videos = (
            Video.objects.all()
            .values(month=TruncMonth("release_date"))
            .annotate(
                count=Count("pk", distinct=True),
            )
            .order_by("month")
        )
        months = [
            {
                "month": i["month"].strftime("%b '%y"),
                "count": i["count"],
            }
            for i in videos
        ]

        data = OrderedDict()

        for month in months:
            data[month["month"]] = (month["count"],)

        context = {
            "bar_data": {
                "labels": list(data.keys()),
                "datasets": [
                    {
                        "label": " Video",
                        "data": [x[0] for x in data.values()],
                    },
                ],
            },
            "bar_fallback": list(data.items()),
            "bar_title": "Videos per Month",
        }

        return context

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_show_count())
        context.update(self.get_monthly_count())
        return context


class BirthdayGamesDaily(TemplateView):
    http_method_names = "get"
    template_name = "videos/partials/get-kfgd-birthdays.html"

    def get_context_data(self, **kwargs):  # pragma: no cover
        context = super().get_context_data(**kwargs)

        videos = cache.get(self.request.build_absolute_uri())

        if not videos:
            videos = videos = (
                Video.objects.values("link", "title")
                .filter(
                    Q(release_date__month=self.request.GET.get("month", ""))
                    & Q(release_date__day=self.request.GET.get("day", ""))
                    & Q(show__slug="kfgd")
                    & Q(channel__slug="games")
                )
                .order_by("-release_date")
            )
            cache.set(
                self.request.build_absolute_uri(),
                videos,
                60 * 5,  # 5 minutes
            )

        context["videos"] = videos
        return context
        return context

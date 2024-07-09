from datetime import date, timedelta, datetime
from feedparser import parse
from requests import get

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.template.defaultfilters import slugify
from django.utils.crypto import get_random_string
from django.views import View

from .models import Video
from apps.channels.models import Channel
from apps.core.views import DefaultVideoView
from apps.shows.models import Show


class AllVideosView(DefaultVideoView):
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


class UpdateVideosView(LoginRequiredMixin, View):
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
        slug = slugify(title)[:51]

        if Video.objects.filter(video_id=video_id).exists():
            return
        elif Video.objects.filter(slug=slug).exists():
            slug = f"{slug}-{get_random_string(length=2)}"

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
            slug=slug,
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
        url_1 = (
            f"https://youtube.googleapis.com/youtube/v3/search?key="
            f"{API_KEY}&channelId={channel}&part=snippet&maxResults="
            f"{max_results}&pageToken={page}&order=date&type=video&"
            f"publishedBefore={published_before}&publishedAfter="
            f"{published_after}"
        )
        response = get(url=url_1).json()
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

            url_2 = (
                "https://youtube.googleapis.com/youtube/v3/videos?part="
                f"contentDetails%2Csnippet&id={video_id}&key={API_KEY}"
            )
            vid = get(url=url_2).json()["items"][0]

            blurb = vid["snippet"]["description"]
            release_date = datetime.fromisoformat(
                vid["snippet"]["publishedAt"]
            ).date()
            duration = vid["contentDetails"]["duration"]

            if "M" in duration or "H" in duration:
                link = f"https://www.youtube.com/watch?v={video_id}"
                short = False
            else:
                link = f"https://www.youtube.com/shorts/{video_id}"
                short = True

            self.create_video(
                video_id=video_id,
                title=title,
                release_date=release_date,
                link=link,
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

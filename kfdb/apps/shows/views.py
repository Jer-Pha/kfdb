from collections import OrderedDict
from django.core.cache import cache
from django.db.models import Count, F, Prefetch, Q
from django.db.models.functions import TruncMonth
from django.views.generic import TemplateView

from .models import Show
from apps.channels.models import Channel
from apps.core.views import DefaultVideoView
from apps.hosts.models import Host
from apps.videos.models import Video


class ShowsHomeView(TemplateView):
    http_method_names = "get"
    template_name = ""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.template_name = (
            "shows/shows-home.html"
            if "Hx-Request" not in self.request.headers
            else "shows/partials/show-logo-scroller.html"
        )

        games = cache.get("shows_games")
        if not games:
            games = (
                Show.objects.only("name", "slug", "image")
                .filter(channels__slug="games")
                .order_by("-active", "name")
            )
            cache.set(
                "shows_games",
                games,
                60 * 15,  # 15 minutes
            )

        prime = cache.get("shows_prime")
        if not prime:
            prime = (
                Show.objects.only("name", "slug", "image")
                .filter(channels__slug="prime")
                .order_by("-active", "name")
            )
            cache.set(
                "shows_prime",
                prime,
                60 * 15,  # 15 minutes
            )

        members = cache.get("shows_members")
        if not members:
            members = (
                Show.objects.only("name", "slug", "image")
                .filter(channels__slug="members")
                .order_by("-active", "name")
            )
            cache.set(
                "shows_members",
                members,
                60 * 15,  # 15 minutes
            )

        context.update(
            {
                "games": games,
                "prime": prime,
                "members": members,
            }
        )

        return context


class ShowPageView(DefaultVideoView):
    template_name = ""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.template_name = (
            "shows/show-page.html"
            if self.new_page
            else "videos/partials/get-video-results.html"
        )
        show = (
            Show.objects.prefetch_related(
                Prefetch(
                    "channels",
                    queryset=Channel.objects.only("name", "slug").all(),
                ),
            )
            .only("name", "blurb", "image", "channels")
            .get(slug=kwargs.get("show", ""))
        )
        filter_params = {"show": show.id}
        videos = cache.get(self.request.build_absolute_uri())

        if not videos:
            videos = self.get_videos(filter_params)
            cache.set(
                self.request.build_absolute_uri(),
                videos,
                60 * 5,  # 5 minutes
            )
        context["videos"] = videos

        if self.new_page:
            if "?channel=" in self.request.build_absolute_uri():
                channel = (
                    f'&{self.request.build_absolute_uri().split("?", 1)[1]}'
                )
            else:
                channel = ""
            context.update(
                {
                    "show": show,
                    "filter_param": f"s={show.id}" + channel,
                    "channel": channel,
                }
            )

        return context


class ShowChartsView(TemplateView):
    http_method_names = "get"
    template_name = "core/partials/get-charts.html"

    def get_host_count(self, show):
        """Calculates host appearances for selected show."""
        if self.channel:
            hosts = Host.objects.filter(
                video_host__show=show,
                video_host__channel__slug=self.channel,
            )
            producers = Host.objects.filter(
                video_producer__show=show,
                video_producer__channel__slug=self.channel,
            )
        else:
            hosts = Host.objects.filter(video_host__show=show)
            producers = Host.objects.filter(video_producer__show=show)

        hosts = list(
            hosts.annotate(count=Count("video_host", distinct=True))
            .values("name", "count")
            .order_by("-count")
        )
        producers = list(
            producers.annotate(count=Count("video_producer", distinct=True))
            .values("name", "count")
            .order_by("-count")
        )
        producers = {p["name"]: p["count"] for p in producers}

        data = {}
        other_count = 0

        for host in hosts:
            if len(data) < 10 and host["name"] in producers:
                data[host["name"]] = host["count"] + producers.pop(
                    host["name"]
                )
            elif len(data) < 10:
                data[host["name"]] = host["count"]
            elif host["name"] in producers:
                other_count += host["count"] + producers.pop(host["name"])
            else:
                other_count += host["count"]

        for name, count in producers.items():
            if len(data) < 10:
                data[name] = count
            else:
                other_count += count

        if other_count:
            data["Other"] = other_count

        context = {
            "doughnut_data": {
                "labels": list(data.keys()),
                "datasets": [
                    {
                        "label": " Appearances",
                        "data": list(data.values()),
                        "borderWidth": 1,
                    },
                ],
            },
            "doughnut_fallback": list(data.items()),
            "doughnut_title": "Appearances",
        }

        return context

    def get_monthly_count(self, show):
        """Calculates episodes per month for selected show."""
        if self.channel:
            videos = Video.objects.filter(
                show=show,
                channel__slug=self.channel,
            )
        else:
            videos = Video.objects.filter(
                show=show,
                channel__in=(
                    list(show.channels.all().values_list("pk", flat=True))
                ),
            )

        videos = (
            videos.values(month=TruncMonth("release_date"))
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
        show = Show.objects.only("pk", "channels", "channels__id").get(
            id=int(self.request.GET.get("show", ""))
        )
        self.channel = self.request.GET.get("channel", "")
        if self.channel.lower() in (
            "prime",
            "games",
        ) or (
            not self.channel
            and show.channels.all().values_list("pk", flat=True) != [3]
        ):
            context.update(self.get_host_count(show))
        context.update(self.get_monthly_count(show))
        return context

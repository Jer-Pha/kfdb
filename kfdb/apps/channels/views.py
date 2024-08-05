from collections import OrderedDict

from django.core.cache import cache
from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.generic import TemplateView

from .models import Channel
from apps.core.views import DefaultVideoView
from apps.shows.models import Show
from apps.videos.models import Video


class ChannelPageView(DefaultVideoView):
    template_name = ""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.template_name = (
            "channels/channel-page.html"
            if self.new_page
            else "videos/partials/get-video-results.html"
        )
        channel = Channel.objects.only("name", "blurb", "image").get(
            slug=kwargs.get("channel", "")
        )
        filter_params = {"channel": channel.id}
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
            context.update(
                {
                    "channel": channel,
                    "filter_param": f"c={channel.id}",
                }
            )

        return context


@method_decorator(
    cache_page(60 * 5, key_prefix="host_chart_data"),
    name="dispatch",
)
class ChannelChartsView(TemplateView):
    http_method_names = "get"
    template_name = "core/partials/get-charts.html"

    def get_show_count(self, channel):
        """Calculates videos per show."""
        shows = list(
            Show.objects.filter(channels=channel)
            .annotate(count=Count("video_show", distinct=True))
            .values("name", "count")
            .order_by("-count")
            .distinct()
        )

        multiples = list(
            Show.objects.annotate(channel_count=Count("channels"))
            .filter(channels=channel, channel_count__gt=1)
            .values_list("name", flat=True)
        )

        data = {}
        other = 0

        for show in shows:
            name = show["name"]
            if name in multiples:
                count = (
                    Video.objects.only("pk")
                    .filter(channel=channel, show__name=name)
                    .count()
                )
            else:
                count = show["count"]
            if len(data) < 10:
                data[name] = count
            else:
                other += count

        data = OrderedDict(
            sorted(
                data.items(),
                key=lambda i: i[1],
                reverse=True,
            )
        )

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

    def get_monthly_count(self, channel):
        """Calculates episodes per month for all videos."""
        videos = (
            Video.objects.filter(channel=channel)
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
        channel = Show.objects.values_list("pk", flat=True).get(
            id=int(self.request.GET.get("channel", ""))
        )
        context.update(self.get_show_count(channel))
        context.update(self.get_monthly_count(channel))
        return context

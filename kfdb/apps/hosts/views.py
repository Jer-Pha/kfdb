from collections import OrderedDict
from re import sub

from django.core.cache import cache
from django.core.paginator import Paginator
from django.db.models import Count, F, Q
from django.db.models.functions import TruncMonth
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.generic import TemplateView

from .models import Host
from apps.core.views import DefaultVideoView
from apps.shows.models import Show
from apps.videos.models import Video


class HostPageView(DefaultVideoView):
    template_name = ""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.template_name = (
            "hosts/host-page.html"
            if self.new_page
            else "videos/partials/get-video-results.html"
        )
        host = Host.objects.defer("image_xs", "kf_crew", "part_timer").get(
            slug=kwargs.get("host", "")
        )
        filter_params = {"host": host.id}
        videos = cache.get(self.request.build_absolute_uri())
        self.page_range = cache.get(
            f"{self.request.build_absolute_uri()}_page_range"
        )

        if not videos:
            videos = self.get_videos(filter_params)
            cache.set(
                self.request.build_absolute_uri(),
                videos,
                60 * 5,  # 5 minutes
            )
            cache.set(
                f"{self.request.build_absolute_uri()}_page_range",
                self.page_range,
                60 * 5,  # 5 minutes
            )
        context["videos"] = videos

        if self.new_page:
            context.update(
                {
                    "host": host,
                    "filter_param": f"h={host.id}",
                }
            )

        return context


class BaseHostView(TemplateView):
    http_method_names = "get"
    template_name = ""

    def get(self, request, **kwargs):
        self.curr_path = request.path
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def get_hosts(self, hosts):
        new_page = "Hx-Request" not in self.request.headers
        if new_page:
            self.template_name = "hosts/hosts-home.html"
            results_per_page = 30
        else:
            self.template_name = "hosts/partials/get-hosts.html"
            results_per_page = 12

        hosts = (
            hosts.defer(
                "nicknames", "socials", "birthday", "blurb", "image_xs"
            )
            .annotate(
                count_hosted=Count("video_host", distinct=True),
                count_produced=Count("video_producer", distinct=True),
                appearances=(F("count_hosted") + F("count_produced")),
            )
            .order_by(
                *(
                    self.request.GET.get(
                        "sort", "-kf_crew,-part_timer,name"
                    ).split(",")
                )
            )
        )

        search = sub(" +", " ", self.request.GET.get("search", "").strip())

        if search:
            hosts = hosts.filter(
                Q(name__icontains=search)
                | Q(slug__icontains=search.replace(" ", "-"))
            )
        else:
            hosts = hosts.all()

        page = int(self.request.GET.get("page", 1))
        paginator = Paginator(hosts, results_per_page)
        self.last_page = paginator.num_pages <= page
        hosts = paginator.get_page(page).object_list

        if new_page:
            page = 6
        else:
            page += 1

        self.page = page

        return hosts


@method_decorator(
    cache_page(60 * 15, key_prefix="hosts_all"),
    name="dispatch",
)
class HostsHomeView(BaseHostView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        hosts = Host.objects
        hosts = self.get_hosts(hosts)

        context.update(
            {
                "hosts": hosts,
                "host_type": "All Hosts",
            }
        )

        return context


@method_decorator(
    cache_page(60 * 5, key_prefix="hosts_crew"),
    name="dispatch",
)
class HostCrewView(BaseHostView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        hosts = Host.objects.filter(kf_crew=True, part_timer=False)
        hosts = self.get_hosts(hosts)

        context.update(
            {
                "hosts": hosts,
                "host_type": "KF Crew",
            }
        )

        return context


@method_decorator(
    cache_page(60 * 5, key_prefix="hosts_part_timers"),
    name="dispatch",
)
class HostPartTimerView(BaseHostView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        hosts = Host.objects.filter(kf_crew=False, part_timer=True)
        hosts = self.get_hosts(hosts)

        context.update(
            {
                "hosts": hosts,
                "host_type": "Part Timers",
            }
        )

        return context


@method_decorator(
    cache_page(60 * 15, key_prefix="hosts_guests"),
    name="dispatch",
)
class HostGuestView(BaseHostView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        hosts = Host.objects.filter(kf_crew=False, part_timer=False)
        hosts = self.get_hosts(hosts)

        context.update(
            {
                "hosts": hosts,
                "host_type": "Guests",
            }
        )

        return context


@method_decorator(
    cache_page(60 * 5, key_prefix="random_hosts"),
    name="dispatch",
)
class RandomHostsView(TemplateView):
    http_method_names = "get"
    template_name = "core/partials/get-host-names.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        hosts = (
            Host.objects.filter(kf_crew=False)
            .order_by("?")
            .values_list("name", flat=True)
        )

        context.update(
            {
                "hosts": hosts,
            }
        )

        return context


@method_decorator(
    cache_page(60 * 5, key_prefix="host_chart_data"),
    name="dispatch",
)
class HostChartsView(TemplateView):
    http_method_names = "get"
    template_name = "core/partials/get-charts.html"

    def get_appearance_count(self, host):
        """Calculates appearances per show for selected host."""
        shows = list(
            Show.objects.filter(
                Q(video_show__hosts=host) | Q(video_show__producer=host)
            )
            .annotate(count=Count("video_show", distinct=True))
            .values("name", "count")
            .order_by("-count")
            .distinct()
        )

        data = {}
        other = 0

        for show in shows:
            if len(data) < 9:
                data[show["name"]] = show["count"]
            else:
                other += show["count"]

        if other:
            data["Other"] = other

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
        }

        return context

    def get_app_prod_dates(self, host):
        """Calculates episodes per month for selected host for both
        appearances and produced episodes.
        """
        videos = (
            Video.objects.filter(Q(hosts=host) | Q(producer=host))
            .values(month=TruncMonth("release_date"))
            .annotate(
                host_count=Count("pk", filter=Q(hosts=host), distinct=True),
                producer_count=Count(
                    "pk",
                    filter=Q(producer=host),
                    distinct=True,
                ),
            )
            .order_by("month")
        )
        months = [
            {
                "month": i["month"].strftime("%b '%y"),
                "host_count": i["host_count"],
                "producer_count": i["producer_count"],
            }
            for i in videos
        ]

        data = OrderedDict()

        for month in months:
            data[month["month"]] = (
                month["host_count"],
                month["producer_count"],
            )

        context = {
            "bar_data": {
                "labels": list(data.keys()),
                "datasets": [
                    {
                        "label": " Appeared ",
                        "data": [x[0] for x in data.values()],
                    },
                    {
                        "label": " Produced",
                        "data": [x[1] for x in data.values()],
                    },
                ],
            },
            "bar_fallback": list(data.items()),
        }

        return context

    def get_appearance_dates(self, host):
        """Calculates episodes per month for selected host for only
        appearances.
        """
        videos = (
            Video.objects.filter(Q(hosts=host) | Q(producer=host))
            .values(month=TruncMonth("release_date"))
            .annotate(
                host_count=Count("pk", filter=Q(hosts=host), distinct=True),
            )
            .order_by("month")
        )
        months = [
            {
                "month": i["month"].strftime("%b '%y"),
                "host_count": i["host_count"],
            }
            for i in videos
        ]

        data = OrderedDict()

        for month in months:
            data[month["month"]] = (month["host_count"],)

        context = {
            "bar_data": {
                "labels": list(data.keys()),
                "datasets": [
                    {
                        "label": " Appearance",
                        "data": [x[0] for x in data.values()],
                    },
                ],
            },
            "bar_fallback": list(data.items()),
        }

        return context

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        host = Host.objects.get(id=int(self.request.GET.get("host", "")))
        context.update(self.get_appearance_count(host))
        if Video.objects.filter(producer=host).exists():
            context.update(self.get_app_prod_dates(host))
        else:
            context.update(self.get_appearance_dates(host))
        return context

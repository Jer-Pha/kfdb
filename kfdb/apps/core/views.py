from re import sub

from django.conf import settings
from django.core.paginator import Paginator
from django.db.models import Count, Prefetch, Q
from django.http import HttpResponse
from django.shortcuts import render
from django.views import View
from django.views.decorators.http import require_GET
from django.views.generic import TemplateView

from apps.channels.models import Channel
from apps.core.utils import Filter
from apps.hosts.models import Host
from apps.videos.models import Video


class DefaultVideoView(TemplateView):
    http_method_names = "get"

    def get(self, request, **kwargs):
        self.new_page = (
            "Hx-Boosted" in request.headers
            or not "Hx-Request" in request.headers
        )
        self.curr_path = request.path
        self.page = int(request.GET.get("page", 1))
        self.sort = request.GET.get("sort", "-release_date")
        self.search = sub(" +", " ", request.GET.get("search", "").strip())
        self.filter_channel = request.GET.get("channel", "")
        self.filter_show = request.GET.get("show", "")
        self.filter_guest = request.GET.get("guest", "")
        self.filter_producer = request.GET.get("producer", "")
        self.filter_part_timer = request.GET.get("part-timer", "")
        self.filter_crew = dict(request.GET).get("crew", [])
        self.results_per_page = request.GET.get("results", 25)
        self.videos = Video.objects
        context = self.get_context_data(**kwargs)

        return self.render_to_response(context)

    def build_filter(self, filter_params):
        if self.filter_channel:
            self.videos = self.videos.select_related("channel")
            filter_params["channel__slug"] = self.filter_channel

        if self.filter_show:
            self.videos = self.videos.select_related("show")
            filter_params["show__slug"] = self.filter_show

        if self.filter_producer:
            filter_params["producer__slug"] = self.filter_producer

        if self.search and not settings.DEBUG:
            self.videos = self.videos.filter(
                Q(blurb__search=self.search) | Q(title__search=self.search)
            )
        elif self.search:
            self.videos = self.videos.filter(
                Q(blurb__icontains=self.search)
                | Q(title__icontains=self.search)
            )

        if self.filter_crew:
            if self.filter_guest:
                self.filter_crew.append(self.filter_guest)
            if self.filter_part_timer:
                self.filter_crew.append(self.filter_part_timer)

            self.videos = self.videos.prefetch_related(
                Prefetch(
                    "hosts",
                    queryset=Host.objects.only("slug").filter(
                        slug__in=self.filter_crew
                    ),
                )
            )

            for host in self.filter_crew:
                self.videos = self.videos.filter(hosts__slug=host)
        else:
            self.videos = self.videos.prefetch_related(
                Prefetch(
                    "hosts",
                    queryset=Host.objects.only("slug").filter(
                        slug__in=[self.filter_guest, self.filter_part_timer]
                    ),
                )
            )
            if self.filter_guest:
                self.videos = self.videos.filter(hosts__slug=self.filter_guest)
            if self.filter_part_timer:
                self.videos = self.videos.filter(
                    hosts__slug=self.filter_part_timer
                )

        return filter_params

    def get_videos(self, filter_params):
        filter_params = self.build_filter(filter_params)
        print(filter_params)

        videos = (
            self.videos.filter(**filter_params)
            .only(
                "title",
                "video_id",
                "release_date",
                "show",
                "show__name",
                "show__image",
                "channel",
            )
            .order_by(self.sort)
        )

        paginator = Paginator(videos, self.results_per_page)
        page_count = paginator.num_pages
        videos = paginator.get_page(self.page).object_list

        return videos


class HeroStatsView(TemplateView):
    http_method_names = "get"
    template_name = "core/partials/update-index-stats.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        count = Host.objects.only("pk", "kf_crew", "part_timer").aggregate(
            crew=Count("pk", filter=Q(kf_crew=True, part_timer=False)),
            pt=Count("pk", filter=Q(kf_crew=False, part_timer=True)),
            guest=Count("pk", filter=Q(kf_crew=False, part_timer=False)),
        )
        count["video"] = Video.objects.all().count()
        context["count"] = count
        return context


class VideoDetailsView(TemplateView):
    http_method_names = "get"
    template_name = "core/partials/get-video-details.html"

    def get(self, request, **kwargs):
        self.video_id = request.GET.get("video_id", "")
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        video = (
            Video.objects.select_related("show", "producer", "channel")
            .prefetch_related("hosts")
            .get(video_id=self.video_id)
        )
        context["video"] = video
        return context


class BuildFilterView(TemplateView):
    http_method_names = "get"
    template_name = "core/partials/build-filter.html"

    def get(self, request, **kwargs):
        context = self.get_context_data(**kwargs)
        if "c" in request.GET:
            context.update(
                Filter(
                    channel_id=int(request.GET.get("c", 0))
                ).channel_filter()
            )
        elif "s" in request.GET:
            context.update(
                Filter(show_id=int(request.GET.get("s", 0))).show_filter()
            )
        elif "h" in request.GET:
            context.update(
                Filter(host_id=int(request.GET.get("h", 0))).host_filter()
            )
        else:
            context.update(Filter().host_filter())

        context["curr_path"] = request.GET.get("u", "")
        return self.render_to_response(context)


class UpdateThemeView(View):
    http_method_names = "get"

    def get(self, request):
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

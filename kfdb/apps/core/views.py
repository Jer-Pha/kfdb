from re import sub
from sys import argv

from django.conf import settings
from django.core.paginator import Paginator
from django.db.models import Count, Prefetch, Q
from django.db.models.functions import Lower
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import cache_page
from django.views.generic import TemplateView

from apps.core.utils import Filter
from apps.hosts.models import Host
from apps.shows.models import Show
from apps.videos.models import Video


class DefaultVideoView(TemplateView):
    http_method_names = "get"

    def get(self, request, **kwargs):
        self.new_page = "Hx-Request" not in request.headers
        self.curr_path = request.path
        self.page = int(request.GET.get("page", 1))
        self.videos = Video.objects
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def build_filter(self, filter_params):
        filter_channel = self.request.GET.get("channel", "")
        filter_show = self.request.GET.get("show", "")
        filter_producer = self.request.GET.get("producer", "")
        search = sub(" +", " ", self.request.GET.get("search", "").strip())
        filter_crew = dict(self.request.GET).get("crew", [])
        filter_part_timer = self.request.GET.get("part-timer", "")
        filter_guest = self.request.GET.get("guest", "")

        if filter_channel:
            filter_params["channel__slug"] = filter_channel
        if filter_show:
            filter_params["show__slug"] = filter_show
        if filter_producer:
            filter_params["producer__slug"] = filter_producer

        if search and not settings.DEBUG and "test" not in argv:
            self.videos = self.videos.filter(  # pragma: no cover
                Q(blurb__search=search) | Q(title__search=search)
            )
        elif search:
            self.videos = self.videos.filter(
                Q(blurb__icontains=search) | Q(title__icontains=search)
            )

        if filter_crew:
            if filter_guest:
                filter_crew.append(filter_guest)
            if filter_part_timer:
                filter_crew.append(filter_part_timer)

            self.videos = self.videos.prefetch_related(
                Prefetch(
                    "hosts",
                    queryset=Host.objects.only("slug").filter(
                        slug__in=filter_crew
                    ),
                )
            )

            for host in filter_crew:
                self.videos = self.videos.filter(hosts__slug=host)
        else:
            self.videos = self.videos.prefetch_related(
                Prefetch(
                    "hosts",
                    queryset=Host.objects.only("slug").filter(
                        slug__in=[filter_guest, filter_part_timer]
                    ),
                )
            )
            if filter_guest:
                self.videos = self.videos.filter(hosts__slug=filter_guest)
            if filter_part_timer:
                self.videos = self.videos.filter(hosts__slug=filter_part_timer)

        if "host" in filter_params:
            host = filter_params.pop("host")
            self.videos = self.videos.filter(
                Q(hosts=host) | Q(producer=host)
            ).distinct()

        return filter_params

    def get_videos(self, filter_params):
        filter_params = self.build_filter(filter_params)
        sort = self.request.GET.get("sort", "-release_date")

        if sort != "-release_date" and sort[0] == "-":
            sort = Lower(sort[1:]).desc()
        elif sort not in ("release_date", "-release_date"):
            sort = Lower(sort)

        videos = (
            self.videos.filter(**filter_params)
            .prefetch_related("show")
            .only(
                "title",
                "video_id",
                "release_date",
                "show",
                "show__name",
                "show__slug",
                "show__image_xs",
                "channel",
            )
            .order_by(sort)
        )

        paginator = Paginator(videos, self.request.GET.get("results", 25))
        self.get_page_range(self.page, paginator.num_pages)
        videos = paginator.get_page(self.page).object_list

        return videos

    def get_page_range(self, page, page_count):
        if page < 3 and page_count > 5:
            self.page_range = list(range(1, 4))
            self.page_range.extend(("...", page_count))
        elif page_count > 1 and page_count < 6:
            self.page_range = range(1, page_count + 1)
        elif page_count > 5 and page > 2 and page < page_count - 1:
            self.page_range = [1, "..."]
            self.page_range.extend(list(range(page - 1, page + 2)))
            self.page_range.extend(("...", page_count))
        elif page_count > 5 and page >= page_count - 1:
            self.page_range = [1, "..."]
            self.page_range.extend(list(range(page_count - 2, page_count + 1)))
        else:
            self.page_range = None
        self.page_count = page_count


@method_decorator(cache_page(60 * 15), name="dispatch")
class HostCountView(TemplateView):
    http_method_names = "get"
    template_name = "core/partials/get-host-count.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        count = Host.objects.only("pk", "kf_crew", "part_timer").aggregate(
            crew=Count("pk", filter=Q(kf_crew=True, part_timer=False)),
            pt=Count("pk", filter=Q(kf_crew=False, part_timer=True)),
            guest=Count("pk", filter=Q(kf_crew=False, part_timer=False)),
        )
        context["count"] = count

        return context


@method_decorator(cache_page(60 * 15), name="dispatch")
class HeroStatsView(HostCountView):
    http_method_names = "get"
    template_name = "core/partials/update-index-stats.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["count"]["video"] = Video.objects.all().count()
        return context


@method_decorator(cache_page(60 * 15), name="dispatch")
class ShowCountView(View):
    http_method_names = "get"

    def get(self, request):
        return HttpResponse(Show.objects.only("pk").all().count(), status=200)


@method_decorator(cache_page(60 * 15), name="dispatch")
class BuildFilterView(TemplateView):
    http_method_names = "get"
    template_name = "core/partials/generate-filters.html"

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
            context["channel"] = request.GET.get("channel", "")
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
        else:  # pragma: no cover
            return HttpResponse(status=304)

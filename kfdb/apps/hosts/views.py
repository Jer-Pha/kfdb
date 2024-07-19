from re import sub

from django.core.paginator import Paginator
from django.db.models import Count, F, Q
from django.views.generic import TemplateView

from .models import Host
from apps.core.views import DefaultVideoView


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
        context["videos"] = self.get_videos(filter_params)
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

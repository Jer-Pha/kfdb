from django.db.models import Count, F
from django.http import HttpResponse
from django.views.generic import TemplateView

from .models import Host
from apps.core.views import DefaultVideoView


def host_home(request):
    return HttpResponse()


def host_type(request, type):
    return HttpResponse()


class HostPageView(DefaultVideoView):
    template_name = ""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.template_name = (
            "hosts/host-page.html"
            if self.new_page
            else "core/partials/get-video-results.html"
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


class HostHomeView(TemplateView):
    template_name = "hosts/hosts-home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        hosts = (
            Host.objects.all()
            .defer("nicknames", "socials", "birthday", "blurb", "image_xs")
            .annotate(
                count_hosted=Count("video_host", distinct=True),
                count_produced=Count("video_producer", distinct=True),
                appearances=(F("count_hosted") + F("count_produced")),
            )
            .order_by("-kf_crew", "-part_timer", "name")
        )

        context.update(
            {
                "hosts": hosts,
                "host_type": "All",
            }
        )

        return context

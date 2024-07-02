from django.db.models import Q
from django.http import HttpResponse

from .models import Host
from apps.core.views import DefaultVideoView
from apps.videos.models import Video


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
                    "appearances": (
                        Video.objects.only("id")
                        .filter(Q(hosts=host) | Q(producer=host))
                        .count()
                    ),
                }
            )

        return context

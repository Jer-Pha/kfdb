from django.http import HttpResponse

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
        host = Host.objects.values("id", "name", "blurb").get(
            slug=kwargs.get("host", "")
        )
        filter_params = {"hosts": host["id"]}
        context["videos"] = self.get_videos(filter_params)
        if self.new_page:
            context.update(
                {
                    "host": host,
                    "curr_path": self.curr_path,
                }
            )

        return context

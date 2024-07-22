from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from .models import Channel
from apps.core.views import DefaultVideoView


@method_decorator(cache_page(60 * 15), name="dispatch")
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
        context["videos"] = self.get_videos(filter_params)
        if self.new_page:
            context.update(
                {
                    "channel": channel,
                    "filter_param": f"c={channel.id}",
                }
            )

        return context

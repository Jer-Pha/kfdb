from django.core.cache import cache

from .models import Channel
from apps.core.views import DefaultVideoView


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
                60 * 15,  # 15 minutes
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

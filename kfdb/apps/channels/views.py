from django.shortcuts import render

from .models import Channel
from apps.core.views import DefaultVideoView


class ChannelPageView(DefaultVideoView):
    template_name = ""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.template_name = (
            "channels/channel-page.html"
            if self.new_page
            else "core/partials/get-video-results.html"
        )
        channel = Channel.objects.values("id", "name", "blurb").get(
            slug=kwargs.get("channel", "")
        )
        filter_params = {"channel": channel["id"]}
        context["videos"] = self.get_videos(filter_params)
        if self.new_page:
            context.update(
                {
                    "channel": channel,
                    "filter_param": f"c={channel['id']}",
                }
            )

        return context

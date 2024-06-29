from apps.core.views import DefaultVideoView


class ChannelPageView(DefaultVideoView):
    template_name = ""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.template_name = (
            "videos/videos-home.html"
            if self.new_page
            else "core/partials/get-video-results.html"
        )
        filter_params = {}
        context["videos"] = self.get_videos(filter_params)
        if self.new_page:
            context.update(
                {
                    "curr_path": self.curr_path,
                }
            )

        return context

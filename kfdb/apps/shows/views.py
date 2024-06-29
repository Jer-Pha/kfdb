from .models import Show
from apps.core.views import DefaultVideoView


class ShowPageView(DefaultVideoView):
    template_name = ""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.template_name = (
            "shows/show-page.html"
            if self.new_page
            else "core/partials/get-video-results.html"
        )
        show = Show.objects.values("id", "name", "blurb").get(
            slug=kwargs.get("show", "")
        )
        filter_params = {"show": show["id"]}
        context["videos"] = self.get_videos(filter_params)
        if self.new_page:
            context.update(
                {
                    "show": show,
                    "curr_path": self.curr_path,
                }
            )

        return context

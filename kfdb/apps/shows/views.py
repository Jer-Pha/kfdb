from django.db.models import Prefetch
from django.views.generic import TemplateView

from .models import Show
from apps.channels.models import Channel
from apps.core.views import DefaultVideoView


class ShowsHomeView(TemplateView):
    template_name = ""

    def get(self, request, **kwargs):
        self.new_page = (
            "Hx-Boosted" in request.headers
            or not "Hx-Request" in request.headers
        )
        context = self.get_context_data(**kwargs)

        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.template_name = (
            "shows/shows-home.html"
            if self.new_page
            else "shows/partials/show-logo-scroller.html"
        )

        games = (
            Show.objects.only("name", "slug", "image")
            .filter(channels__slug="games")
            .order_by("-active", "name")
        )

        prime = (
            Show.objects.only("name", "slug", "image")
            .filter(channels__slug="prime")
            .order_by("-active", "name")
        )

        members = (
            Show.objects.only("name", "slug", "image")
            .filter(channels__slug="members")
            .order_by("-active", "name")
        )

        context.update(
            {
                "games": games,
                "prime": prime,
                "members": members,
            }
        )

        return context


class ShowPageView(DefaultVideoView):
    template_name = ""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.template_name = (
            "shows/show-page.html"
            if self.new_page
            else "core/partials/get-video-results.html"
        )
        show = (
            Show.objects.prefetch_related(
                Prefetch(
                    "channels",
                    queryset=Channel.objects.only("name", "slug").all(),
                ),
            )
            .only("name", "blurb", "image", "channels")
            .get(slug=kwargs.get("show", ""))
        )
        filter_params = {"show": show.id}
        context["videos"] = self.get_videos(filter_params)
        if self.new_page:
            context.update(
                {
                    "show": show,
                    "filter_param": f"s={show.id}",
                }
            )

        return context

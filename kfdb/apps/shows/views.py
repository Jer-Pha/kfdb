from django.core.cache import cache
from django.db.models import Prefetch
from django.views.generic import TemplateView

from .models import Show
from apps.channels.models import Channel
from apps.core.views import DefaultVideoView


class ShowsHomeView(TemplateView):
    http_method_names = "get"
    template_name = ""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.template_name = (
            "shows/shows-home.html"
            if "Hx-Request" not in self.request.headers
            else "shows/partials/show-logo-scroller.html"
        )

        games = cache.get_or_set(
            "shows_games",
            (
                Show.objects.only("name", "slug", "image")
                .filter(channels__slug="games")
                .order_by("-active", "name")
            ),
            60 * 15,  # 15 minutes
        )

        prime = cache.get_or_set(
            "shows_prime",
            (
                Show.objects.only("name", "slug", "image")
                .filter(channels__slug="prime")
                .order_by("-active", "name")
            ),
            60 * 15,  # 15 minutes
        )

        members = cache.get_or_set(
            "shows_members",
            (
                Show.objects.only("name", "slug", "image")
                .filter(channels__slug="members")
                .order_by("-active", "name")
            ),
            60 * 15,  # 15 minutes
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
            else "videos/partials/get-video-results.html"
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
        videos = cache.get_or_set(
            self.request.build_absolute_uri(),
            self.get_videos(filter_params),
            60 * 15,  # 15 minutes
        )
        context["videos"] = videos

        if self.new_page:
            if "?channel=" in self.request.build_absolute_uri():
                channel = (
                    f'&{self.request.build_absolute_uri().split("?", 1)[1]}'
                )
            else:
                channel = ""
            context.update(
                {
                    "show": show,
                    "filter_param": f"s={show.id}" + channel,
                }
            )

        return context

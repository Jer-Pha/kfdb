from datetime import datetime

from django.conf import settings
from django.core import signing
from django.utils.crypto import get_random_string
from django.test import RequestFactory, TestCase
from django.urls import reverse

from ..views import (
    BuildFilterView,
    HeroStatsView,
    HostCountView,
    ShowCountView,
    UpdateThemeView,
)
from apps.channels.models import Channel
from apps.hosts.models import Host
from apps.shows.models import Show
from apps.videos.models import Video
from apps.videos.views import AllVideosView


class CoreViewsTest(TestCase):
    """Tests Core views."""

    def setUp(self):
        """Sets up test data."""

        channel = Channel.objects.create(name="Test Channel")
        crew = Host.objects.create(name="Test Crew", kf_crew=True)
        part_timer = Host.objects.create(
            name="Test Part-Timer",
            part_timer=True,
        )
        guest = Host.objects.create(name="Test Guest")
        producer = Host.objects.create(name="Test Producer", kf_crew=True)
        show = Show.objects.create(name="Test Show")

        for i in range(60):
            video_id = get_random_string(length=11)
            video = Video.objects.create(
                title=f"Test Video ({video_id})",
                release_date=datetime.now().date(),
                show=show,
                channel=channel,
                producer=producer,
                video_id=video_id,
                blurb=get_random_string(length=32),
                link=f"https://www.youtube.com/watch?v={video_id}",
            )
            video.hosts.add(crew)
            if not i % 2:
                video.hosts.add(guest)
            if not i % 3 or not i % 5:
                video.hosts.add(part_timer)

    def test_get_videos(self):
        """Tests get_videos()."""
        tests = [
            {
                "params": (
                    "?page=1&sort=title&search=test%20video"
                    "&channel=test-channel&show=test-show&guest=test-guest"
                    "&producer=test-producer&part-timer=test-part-timer"
                    "&crew=test-crew&results=100"
                ),
                "page_range": None,
                "count": 14,
            },
            {
                "params": (
                    "?page=1&sort=title&search=test%20video"
                    "&channel=test-channel&show=test-show&guest=test-guest"
                    "&producer=test-producer&part-timer=test-part-timer"
                ),
                "page_range": None,
                "count": 14,
            },
            {
                "params": "?page=1&sort=-title&results=10",
                "page_range": [1, 2, 3, "...", 6],
                "count": 10,
            },
            {
                "params": "?page=2&results=25",
                "page_range": range(1, 4),
                "count": 25,
            },
            {
                "params": "?page=3&results=10",
                "page_range": [1, "...", 2, 3, 4, "...", 6],
                "count": 10,
            },
            {
                "params": "?page=6&results=10",
                "page_range": [1, "...", 4, 5, 6],
                "count": 10,
            },
        ]

        for test in tests:
            request = RequestFactory().get(
                reverse("videos_home") + test["params"]
            )
            view = AllVideosView.as_view()(request)
            context = view.context_data
            self.assertIn("videos", context)
            self.assertEqual(context["view"].page_range, test["page_range"])
            self.assertEqual(len(context["videos"]), test["count"])

    def test_hero_stats_view(self):
        """Tests HeroStatsView()."""
        request = RequestFactory().get(reverse("load_stats"))
        view = HeroStatsView.as_view()(request)
        context = view.context_data
        self.assertIn("count", context)
        self.assertIn("crew", context["count"])
        self.assertIn("pt", context["count"])
        self.assertIn("guest", context["count"])
        self.assertIn("video", context["count"])

    def test_host_count_view(self):
        """Tests HostCountView()."""
        request = RequestFactory().get(reverse("get_host_count"))
        view = HostCountView.as_view()(request)
        context = view.context_data
        self.assertIn("count", context)
        self.assertEqual(context["count"]["crew"], 2)
        self.assertEqual(context["count"]["pt"], 1)
        self.assertEqual(context["count"]["guest"], 1)

    def test_show_count_view(self):
        """Tests ShowCountView()."""
        request = RequestFactory().get(reverse("get_show_count"))
        view = ShowCountView()
        view.setup(request)
        response = view.get(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"1")

    def test_build_filter_view(self):
        """Tests BuildFilterView()."""
        channel_id = Channel.objects.values_list("id", flat=True).all().first()
        show_id = Show.objects.values_list("id", flat=True).all().first()
        host_id = Host.objects.values_list("id", flat=True).all().first()
        tests = [
            {
                "params": f"?c={channel_id}&u=/c/prime/",
                "include": [
                    "shows_active",
                    "shows_inactive",
                    "hosts_crew",
                    "hosts_part_timers",
                    "hosts_guests",
                    "hosts_producers",
                ],
                "exclude": ["channels"],
            },
            {
                "params": f"?s={show_id}",
                "include": [
                    "channels",
                    "hosts_crew",
                    "hosts_part_timers",
                    "hosts_guests",
                    "hosts_producers",
                ],
                "exclude": [
                    "shows_active",
                    "shows_inactive",
                ],
            },
            {
                "params": f"?h={host_id}",
                "include": [
                    "channels",
                    "shows_active",
                    "shows_inactive",
                    "hosts_crew",
                    "hosts_part_timers",
                    "hosts_guests",
                    "hosts_producers",
                ],
                "exclude": [],
            },
            {
                "params": "",
                "include": [
                    "channels",
                    "shows_active",
                    "shows_inactive",
                    "hosts_crew",
                    "hosts_part_timers",
                    "hosts_guests",
                    "hosts_producers",
                ],
                "exclude": [],
            },
        ]

        for test in tests:
            request = RequestFactory().get(
                reverse("build_filter") + test["params"]
            )
            view = BuildFilterView.as_view()(request)
            context = view.context_data
            self.assertIn("curr_path", context)
            for key in test["include"]:
                self.assertIn(key, context)
            for key in test["exclude"]:
                self.assertNotIn(key, context)

    def test_update_theme_view(self):
        """Tests UpdateThemeView()."""
        request = RequestFactory().get(reverse("update_theme"))
        view = UpdateThemeView()
        view.setup(request)
        response = view.get(request)
        self.assertEqual(response.status_code, 404)

        request = RequestFactory().get(reverse("update_theme") + "?theme=dark")
        view = UpdateThemeView()
        view.setup(request)
        response = view.get(request)
        self.assertEqual(response.status_code, 200)


class SitemapsTest(TestCase):
    """Tests all sitemaps."""

    def setUp(self):
        """Sets up test data."""

        self.channel = Channel.objects.create(name="Test Channel")
        self.host = Host.objects.create(name="Test Crew", kf_crew=True)
        self.show = Show.objects.create(name="Test Show")

    def test_static_sitemaps(self):
        """Tests static sitemaps."""
        sitemaps = (
            self.client.get("/sitemap.xml"),
            self.client.get("/sitemap-core.xml"),
            self.client.get("/sitemap-priority.xml"),
            self.client.get("/sitemap-static.xml"),
        )
        for response in sitemaps:
            self.assertEqual(response.status_code, 200)

    def test_model_sitemaps(self):
        """Tests model-driven sitemaps."""

        sitemap_hosts = self.client.get("/sitemap-hosts.xml")
        sitemap_shows = self.client.get("/sitemap-shows.xml")
        sitemap_channels = self.client.get("/sitemap-channels.xml")

        self.assertIn(
            f"/hosts/{self.host.url_type}/{self.host.slug}/".encode(),
            sitemap_hosts.content,
        )
        self.assertIn(
            f"/shows/{self.show.slug}/".encode(), sitemap_shows.content
        )
        self.assertIn(
            f"/channels/{self.channel.slug}/".encode(),
            sitemap_channels.content,
        )

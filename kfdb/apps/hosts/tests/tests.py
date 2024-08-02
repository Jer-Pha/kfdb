from datetime import datetime

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory, TestCase
from django.urls import reverse
from rest_framework.test import APIRequestFactory

from ..models import Host
from ..serializers import HostSerializer
from ..views import (
    HostPageView,
    HostCrewView,
    HostGuestView,
    HostsHomeView,
    HostPartTimerView,
    RandomHostsView,
    HostChartsView,
)
from apps.shows.models import Show
from apps.videos.models import Video

# Bytes representing a valid 1-pixel PNG
ONE_PIXEL_PNG_BYTES = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00"
    b"\x01\x08\x04\x00\x00\x00\xb5\x1c\x0c\x02\x00\x00\x00\x0bIDATx"
    b"\x9cc\xfa\xcf\x00\x00\x02\x07\x01\x02\x9a\x1c1q\x00\x00\x00"
    b"\x00IEND\xaeB`\x82"
)


class HostModelTest(TestCase):
    """Tests Host model."""

    def setUp(self):
        """Sets up test data."""
        self.joey = Host.objects.create(
            name="Joey Noelle",
            slug="joey",
            nicknames=["Christmas in >>Current Month<<"],
            kf_crew=True,
            socials=["twitter.com/joeynoelle"],
            birthday=datetime(month=12, day=25, year=2024),
        )
        self.fran = Host.objects.create(
            name="Fran Mirabella III",
            nicknames=["The best hair in the biz"],
            part_timer=True,
            image=SimpleUploadedFile(
                name="test.png",
                content=ONE_PIXEL_PNG_BYTES,
                content_type="image/png",
            ),
        )
        self.xalavier = Host.objects.create(
            name="Xalavier Nelson Jr.",
        )

        video = Video.objects.create(
            title="Test Video",
            video_id="12345678901",
            producer=self.joey,
        )

        video.hosts.add(self.joey, self.fran)

    def test_model_str(self):
        """Tests model __str__."""
        self.assertEqual(str(self.xalavier), self.xalavier.name)

    def test_model_properties(self):
        """Tests model properties."""
        self.assertEqual(self.joey.url_type, "kf-crew")
        self.assertEqual(self.fran.url_type, "part-timers")
        self.assertEqual(self.xalavier.url_type, "guests")
        self.assertEqual(self.joey.initials, "J")
        self.assertEqual(self.fran.initials, "FM3")
        self.assertEqual(self.xalavier.initials, "XN")
        self.assertEqual(self.joey.border_color, "primary")
        self.assertEqual(self.fran.border_color, "secondary")
        self.assertEqual(self.xalavier.border_color, "accent")
        self.assertEqual(
            self.joey.nickname, f"Christmas in {datetime.now().strftime('%B')}"
        )
        self.assertEqual(self.fran.nickname, "The best hair in the biz")
        self.assertEqual(self.xalavier.nickname, "")
        self.assertEqual(self.joey.birth_day, "December 25")
        self.assertEqual(self.fran.appearance_count, 1)
        self.assertEqual(self.joey.appearance_count, 2)


class HostViewsTest(TestCase):
    """Tests Host views."""

    def setUp(self):
        """Sets up test data."""
        h1 = Host.objects.create(
            name="Test Crew",
            slug="test-crew",
            image=SimpleUploadedFile(
                name="test.png",
                content=ONE_PIXEL_PNG_BYTES,
                content_type="image/png",
            ),
            image_xs=SimpleUploadedFile(
                name="test-xs.png",
                content=ONE_PIXEL_PNG_BYTES,
                content_type="image/png",
            ),
            nicknames=["Test Nickname"],
            kf_crew=True,
            part_timer=False,
            socials=["https://www.twitter.com/test"],
            birthday=datetime.now().date(),
            blurb="Test blurb",
        )
        h2 = Host.objects.create(
            name="Test Part Timer",
            slug="test-part-timer",
            image=SimpleUploadedFile(
                name="test.png",
                content=ONE_PIXEL_PNG_BYTES,
                content_type="image/png",
            ),
            image_xs=SimpleUploadedFile(
                name="test-xs.png",
                content=ONE_PIXEL_PNG_BYTES,
                content_type="image/png",
            ),
            nicknames=["Test Nickname"],
            kf_crew=False,
            part_timer=True,
            socials=["https://www.twitter.com/test"],
            birthday=datetime.now().date(),
            blurb="Test blurb",
        )
        h3 = Host.objects.create(
            name="Test Guest",
            slug="test-guest",
            image=SimpleUploadedFile(
                name="test.png",
                content=ONE_PIXEL_PNG_BYTES,
                content_type="image/png",
            ),
            image_xs=SimpleUploadedFile(
                name="test-xs.png",
                content=ONE_PIXEL_PNG_BYTES,
                content_type="image/png",
            ),
            nicknames=["Test Nickname"],
            kf_crew=False,
            part_timer=False,
            socials=["https://www.twitter.com/test"],
            birthday=datetime.now().date(),
            blurb="Test blurb",
        )
        show = Show.objects.create(name="test show")
        v1 = Video.objects.create(
            title="test video 1",
            release_date="2024-01-01",
            show=show,
            producer=h1,
            video_id="12345678900",
        )
        v1.hosts.add(h2, h3)
        v2 = Video.objects.create(
            title="test video 2",
            release_date="2024-02-01",
            show=show,
            video_id="12345678901",
        )
        v2.hosts.add(h1, h2)

    def test_new_page(self):
        """Tests view when `self.new_page == True`."""
        request = RequestFactory().get(
            reverse("host_page", kwargs={"type": "guest", "host": "test-crew"})
        )
        view = HostPageView.as_view()(request, host="test-crew")
        context = view.context_data
        self.assertIn("videos", context)
        self.assertIn("filter_param", context)
        self.assertEqual(context["view"].template_name, "hosts/host-page.html")

    def test_xhr_request(self):
        """Tests view when `self.new_page == False`."""
        request = RequestFactory(headers={"Hx-Request": True}).get(
            reverse(
                "host_page", kwargs={"type": "guest", "host": "test-guest"}
            ),
        )
        view = HostPageView.as_view()(request, host="test-crew")
        context = view.context_data
        self.assertIn("videos", context)
        self.assertNotIn("filter_param", context)
        self.assertEqual(
            context["view"].template_name,
            "videos/partials/get-video-results.html",
        )

    def test_all_hosts_view(self):
        """Tests HostsHomeView()."""
        request = RequestFactory(headers={"Hx-Request": True}).get(
            reverse("hosts_home") + "?search=crew&sort=name&page=2"
        )
        view = HostsHomeView.as_view()(request)
        context = view.context_data
        self.assertIn("hosts", context)
        self.assertEqual(context["host_type"], "All Hosts")

    def test_crew_view(self):
        """Tests HostCrewView()."""
        request = RequestFactory().get(reverse("hosts_crew"))
        view = HostCrewView.as_view()(request)
        context = view.context_data
        self.assertIn("hosts", context)
        self.assertEqual(context["host_type"], "KF Crew")

    def test_part_timers_view(self):
        """Tests HostPartTimerView()."""
        request = RequestFactory().get(reverse("hosts_part_timers"))
        view = HostPartTimerView.as_view()(request)
        context = view.context_data
        self.assertIn("hosts", context)
        self.assertEqual(context["host_type"], "Part Timers")

    def test_guests_view(self):
        """Tests HostGuestView()."""
        request = RequestFactory().get(reverse("hosts_part_timers"))
        view = HostGuestView.as_view()(request)
        context = view.context_data
        self.assertIn("hosts", context)
        self.assertEqual(context["host_type"], "Guests")

    def test_random_hosts_view(self):
        """Tests RandomHostsView()."""
        request = RequestFactory().get(reverse("get_random_hosts"))
        view = RandomHostsView.as_view()(request)
        context = view.context_data
        self.assertIn("hosts", context)
        self.assertEqual(
            len(context["hosts"]), (Host.objects.filter(kf_crew=False).count())
        )

    def test_host_charts_view(self):
        """Tests HostChartsView()."""
        request_1 = RequestFactory().get(reverse("hosts_charts") + "?host=1")
        view = HostChartsView.as_view()(request_1)
        context = view.context_data
        self.assertEqual(
            context["doughnut_data"],
            {
                "labels": ["test show"],
                "datasets": [
                    {
                        "label": " Appearances",
                        "data": [2],
                        "borderWidth": 1,
                    },
                ],
            },
        )
        self.assertEqual(context["doughnut_fallback"], [("test show", 2)])
        self.assertEqual(
            context["bar_data"],
            {
                "labels": ["Jan '24", "Feb '24"],
                "datasets": [
                    {
                        "label": " Appeared ",
                        "data": [0, 1],
                    },
                    {
                        "label": " Produced",
                        "data": [1, 0],
                    },
                ],
            },
        )
        self.assertEqual(
            context["bar_fallback"],
            [("Jan '24", (0, 1)), ("Feb '24", (1, 0))],
        )

        request_2 = RequestFactory().get(reverse("hosts_charts") + "?host=2")
        view_2 = HostChartsView.as_view()(request_2)
        context_2 = view_2.context_data
        self.assertEqual(
            context_2["bar_data"],
            {
                "labels": ["Jan '24", "Feb '24"],
                "datasets": [
                    {
                        "label": " Appearance",
                        "data": [1, 1],
                    },
                ],
            },
        )


class HostSerializerTest(TestCase):
    """Tests Host serializer."""

    def setUp(self):
        """Sets up test data."""
        self.host = Host.objects.create(
            name="Test Host name",
            part_timer=True,
            image_xs=SimpleUploadedFile(
                name="test.png",
                content=ONE_PIXEL_PNG_BYTES,
                content_type="image/png",
            ),
        )

    def test_to_representation(self):
        """Tests custom to_representation()."""
        request_factory = APIRequestFactory()
        request = request_factory.post("/api/hosts/?name=Test+Host+name")
        data = HostSerializer(self.host, context={"request": request}).data
        self.assertEqual(
            data,
            {
                "name": "Test Host name",
                "slug": "test-host-name",
                "part_timer": True,
                "image_xs": f"http://testserver{self.host.image_xs.url}",
            },
        )

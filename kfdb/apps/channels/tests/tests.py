from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.utils.crypto import get_random_string
from rest_framework.test import APIRequestFactory

from ..models import Channel
from ..serializers import ChannelSerializer
from ..views import ChannelChartsView, ChannelPageView
from apps.hosts.models import Host
from apps.shows.models import Show
from apps.videos.models import Video

# Bytes representing a valid 1-pixel PNG
ONE_PIXEL_PNG_BYTES = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00"
    b"\x01\x08\x04\x00\x00\x00\xb5\x1c\x0c\x02\x00\x00\x00\x0bIDATx"
    b"\x9cc\xfa\xcf\x00\x00\x02\x07\x01\x02\x9a\x1c1q\x00\x00\x00"
    b"\x00IEND\xaeB`\x82"
)


class ChannelModelTest(TestCase):
    """Tests Channel model."""

    def setUp(self):
        """Sets up test data."""
        self.channel = Channel.objects.create(
            name="Test Channel name",
        )

    def test_model_str(self):
        """Tests model __str__."""
        self.assertEqual(str(self.channel), self.channel.name)


class ChannelViewsTest(TestCase):
    """Tests Channel views."""

    def setUp(self):
        """Sets up test data."""
        channel_prime = Channel.objects.create(
            name="Prime",
            slug="prime",
            image=SimpleUploadedFile(
                name="test.png",
                content=ONE_PIXEL_PNG_BYTES,
                content_type="image/png",
            ),
        )
        channel_games = Channel.objects.create(
            name="Games",
            slug="games",
            image=SimpleUploadedFile(
                name="test.png",
                content=ONE_PIXEL_PNG_BYTES,
                content_type="image/png",
            ),
        )

        for i in range(12):
            show = Show.objects.create(
                name=f"test show {i}",
            )
            Video.objects.create(
                title=f"Test Video {i}",
                release_date=f"2024-{str(i+1).zfill(2)}-01",
                show=show,
                channel=channel_prime,
                video_id=f"012345678{i}",
            )

        for show in Show.objects.all():
            show.channels.add(channel_prime)

        Show.objects.get(id=1).channels.add(channel_games)

    def test_new_page(self):
        """Tests view when `self.new_page == True`."""
        request = RequestFactory().get(
            reverse("channel_page", kwargs={"channel": "games"})
        )
        view = ChannelPageView.as_view()(request, channel="games")
        context = view.context_data
        self.assertIn("videos", context)
        self.assertIn("filter_param", context)
        self.assertEqual(
            context["view"].template_name, "channels/channel-page.html"
        )

    def test_xhr_request(self):
        """Tests view when `self.new_page == False`."""
        request = RequestFactory(headers={"Hx-Request": True}).get(
            reverse("channel_page", kwargs={"channel": "prime"}),
        )
        view = ChannelPageView.as_view()(request, channel="prime")
        context = view.context_data
        self.assertIn("videos", context)
        self.assertNotIn("filter_param", context)
        self.assertEqual(
            context["view"].template_name,
            "videos/partials/get-video-results.html",
        )

    def test_show_charts_view(self):
        """Tests ChannelChartsView()."""
        self.maxDiff = None
        request = RequestFactory().get(
            reverse("channel_charts") + "?channel=1"
        )
        view = ChannelChartsView.as_view()(request)
        context = view.context_data
        self.assertEqual(
            context["doughnut_data"],
            {
                "labels": [f"test show {i}" for i in range(10)] + ["Other"],
                "datasets": [
                    {
                        "label": " Shows",
                        "data": ([1] * 10) + [2],
                        "borderWidth": 1,
                    },
                ],
            },
        )
        self.assertEqual(
            context["doughnut_fallback"],
            list(
                zip(
                    [f"test show {i}" for i in range(10)] + ["Other"],
                    ([1] * 10) + [2],
                )
            ),
        )
        self.assertEqual(
            context["bar_data"],
            {
                "labels": [
                    "Jan '24",
                    "Feb '24",
                    "Mar '24",
                    "Apr '24",
                    "May '24",
                    "Jun '24",
                    "Jul '24",
                    "Aug '24",
                    "Sep '24",
                    "Oct '24",
                    "Nov '24",
                    "Dec '24",
                ],
                "datasets": [
                    {
                        "label": " Video",
                        "data": [1] * 12,
                    },
                ],
            },
        )
        self.assertEqual(
            context["bar_fallback"],
            list(
                zip(
                    [
                        "Jan '24",
                        "Feb '24",
                        "Mar '24",
                        "Apr '24",
                        "May '24",
                        "Jun '24",
                        "Jul '24",
                        "Aug '24",
                        "Sep '24",
                        "Oct '24",
                        "Nov '24",
                        "Dec '24",
                    ],
                    [(1,)] * 12,
                )
            ),
        )


class ChannelSerializerTest(TestCase):
    """Tests Channel serializer."""

    def setUp(self):
        """Sets up test data."""
        self.channel = Channel.objects.create(
            name="Test Channel name",
            image=SimpleUploadedFile(
                name="test.png",
                content=ONE_PIXEL_PNG_BYTES,
                content_type="image/png",
            ),
        )

    def test_to_representation(self):
        """Tests custom to_representation()."""
        request_factory = APIRequestFactory()
        request = request_factory.post("/api/channels/?name=Test+Channel+name")
        data = ChannelSerializer(
            self.channel, context={"request": request}
        ).data
        self.assertEqual(
            data,
            {
                "name": "Test Channel name",
                "slug": "test-channel-name",
            },
        )

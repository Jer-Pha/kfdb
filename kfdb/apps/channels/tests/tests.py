from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory, TestCase
from django.urls import reverse
from rest_framework.test import APIRequestFactory

from ..models import Channel
from ..serializers import ChannelSerializer
from ..views import ChannelPageView

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
        Channel.objects.create(
            name="Prime",
            slug="prime",
            image=SimpleUploadedFile(
                name="test.png",
                content=ONE_PIXEL_PNG_BYTES,
                content_type="image/png",
            ),
        )
        Channel.objects.create(
            name="Games",
            slug="games",
            image=SimpleUploadedFile(
                name="test.png",
                content=ONE_PIXEL_PNG_BYTES,
                content_type="image/png",
            ),
        )

    def test_new_page(self):
        """Tests view when `self.new_page == True`."""
        request = RequestFactory().get(
            reverse("channel_page", kwargs={"channel": "games"})
        )
        view = ChannelPageView()
        view.setup(request)
        view.get(request, channel="games")
        context = view.get_context_data(channel="games")
        self.assertIn("videos", context)
        self.assertIn("filter_param", context)

    def test_xhr_request(self):
        """Tests view when `self.new_page == False`."""
        request = RequestFactory(headers={"Hx-Request": True}).get(
            reverse("channel_page", kwargs={"channel": "prime"}),
        )
        view = ChannelPageView()
        view.setup(request)
        view.get(request, channel="prime")
        context = view.get_context_data(channel="prime")
        self.assertIn("videos", context)
        self.assertNotIn("filter_param", context)


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
            {"name": "Test Channel name", "slug": "test-channel-name"},
        )

from datetime import datetime

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory, TestCase
from django.urls import reverse
from rest_framework.test import APIRequestFactory

from ..models import Host
from ..serializers import HostSerializer
from ..views import HostPageView

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
        self.host = Host.objects.create(
            name="Test Host name",
            image=SimpleUploadedFile(
                name="test.png",
                content=ONE_PIXEL_PNG_BYTES,
                content_type="image/png",
            ),
        )

    def test_model_str(self):
        """Tests model __str__."""
        self.assertEqual(str(self.host), self.host.name)


class HostViewsTest(TestCase):
    """Tests Host views."""

    def setUp(self):
        """Sets up test data."""
        Host.objects.create(
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
        Host.objects.create(
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
        Host.objects.create(
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

    def test_new_page(self):
        """Tests view when `self.new_page == True`."""
        request = RequestFactory().get(
            reverse("host_page", kwargs={"type": "guest", "host": "test-crew"})
        )
        view = HostPageView()
        view.setup(request)
        view.get(request, host="test-crew")
        context = view.get_context_data(host="test-crew")
        self.assertIn("videos", context)
        self.assertIn("filter_param", context)

    def test_xhr_request(self):
        """Tests view when `self.new_page == False`."""
        request = RequestFactory(headers={"Hx-Request": True}).get(
            reverse(
                "host_page", kwargs={"type": "guest", "host": "test-guest"}
            ),
        )
        view = HostPageView()
        view.setup(request)
        view.get(request, host="test-crew")
        context = view.get_context_data(host="test-crew")
        self.assertIn("videos", context)
        self.assertNotIn("filter_param", context)


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
            },
        )

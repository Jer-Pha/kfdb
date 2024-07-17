from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory, TestCase
from django.urls import reverse
from rest_framework.test import APIRequestFactory

from ..models import Show
from ..serializers import ShowSerializer
from ..views import ShowPageView, ShowsHomeView
from apps.channels.models import Channel

# Bytes representing a valid 1-pixel PNG
ONE_PIXEL_PNG_BYTES = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00"
    b"\x01\x08\x04\x00\x00\x00\xb5\x1c\x0c\x02\x00\x00\x00\x0bIDATx"
    b"\x9cc\xfa\xcf\x00\x00\x02\x07\x01\x02\x9a\x1c1q\x00\x00\x00"
    b"\x00IEND\xaeB`\x82"
)


class ShowModelTest(TestCase):
    """Tests Show model."""

    def setUp(self):
        """Sets up test data."""
        self.show = Show.objects.create(
            name="Test Show name",
            image=SimpleUploadedFile(
                name="test.png",
                content=ONE_PIXEL_PNG_BYTES,
                content_type="image/png",
            ),
        )

    def test_model_str(self):
        """Tests model __str__."""
        self.assertEqual(str(self.show), self.show.name)


class ShowViewsTest(TestCase):
    """Tests Show views."""

    def setUp(self):
        """Sets up test data."""
        show = Show.objects.create(
            name="Test Show",
            slug="test",
            image=SimpleUploadedFile(
                name="test.png",
                content=ONE_PIXEL_PNG_BYTES,
                content_type="image/png",
            ),
            image_xs=SimpleUploadedFile(
                name="test_xs.png",
                content=ONE_PIXEL_PNG_BYTES,
                content_type="image/png",
            ),
            active=True,
            blurb="Test blurb.",
        )

        show.channels.add(
            Channel.objects.create(name="KF Prime", slug="prime"),
            Channel.objects.create(name="KF Games", slug="games"),
            Channel.objects.create(name="KF Membership", slug="members"),
        )

    def test_new_page(self):
        """Tests view when `self.new_page == True`."""
        request = RequestFactory().get(
            reverse("show_page", kwargs={"show": "test"})
        )
        view = ShowPageView.as_view()(request, show="test")
        context = view.context_data
        self.assertIn("videos", context)
        self.assertIn("filter_param", context)
        self.assertEqual(context["view"].template_name, "shows/show-page.html")

    def test_xhr_request(self):
        """Tests view when `self.new_page == False`."""
        request = RequestFactory(headers={"Hx-Request": True}).get(
            reverse("show_page", kwargs={"show": "test"}),
        )
        view = ShowPageView.as_view()(request, show="test")
        context = view.context_data
        self.assertIn("videos", context)
        self.assertNotIn("filter_param", context)
        self.assertEqual(
            context["view"].template_name,
            "core/partials/get-video-results.html",
        )

    def test_all_shows_view(self):
        """Tests ShowsHomeView()."""
        request = RequestFactory().get(reverse("shows_home"))
        view = ShowsHomeView.as_view()(request)
        context = view.context_data
        self.assertIn("games", context)
        self.assertIn("prime", context)
        self.assertIn("members", context)
        self.assertEqual(len(context["games"]), 1)
        self.assertEqual(len(context["prime"]), 1)
        self.assertEqual(len(context["members"]), 1)


class ShowSerializerTest(TestCase):
    """Tests Show serializer."""

    def setUp(self):
        """Sets up test data."""
        self.show = Show.objects.create(
            name="Test Show name",
            active=True,
            image_xs=SimpleUploadedFile(
                name="test.png",
                content=ONE_PIXEL_PNG_BYTES,
                content_type="image/png",
            ),
        )

    def test_to_representation(self):
        """Tests custom to_representation()."""
        request_factory = APIRequestFactory()
        request = request_factory.post("/api/shows/?name=Test+Show+name")
        data = ShowSerializer(self.show, context={"request": request}).data
        self.assertEqual(
            data,
            {
                "name": "Test Show name",
                "slug": "test-show-name",
                "active": True,
            },
        )

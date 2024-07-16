from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from rest_framework.test import APIRequestFactory

from ..models import Show
from ..serializers import ShowSerializer

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

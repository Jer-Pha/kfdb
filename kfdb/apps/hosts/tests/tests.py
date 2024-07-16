from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from rest_framework.test import APIRequestFactory

from ..models import Host
from ..serializers import HostSerializer

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

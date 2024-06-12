from django.test import TestCase
from rest_framework.test import APIRequestFactory

from ..models import Host
from ..serializers import HostSerializer


class HostModelTest(TestCase):
    """Tests Host model."""

    def setUp(self):
        """Sets up test data."""
        self.host = Host.objects.create(
            name="Test Host name",
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
                "kf_crew": False,
                "part_timer": False,
            },
        )

from django.test import TestCase
from rest_framework.test import APIRequestFactory

from ..models import Channel
from ..serializers import ChannelSerializer


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


class ChannelSerializerTest(TestCase):
    """Tests Channel serializer."""

    def setUp(self):
        """Sets up test data."""
        self.channel = Channel.objects.create(
            name="Test Channel name",
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
            {"name": "Test Channel name"},
        )

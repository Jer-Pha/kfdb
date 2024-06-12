from django.test import TestCase
from rest_framework.test import APIRequestFactory

from ..models import Show
from ..serializers import ShowSerializer


class ShowModelTest(TestCase):
    """Tests Show model."""

    def setUp(self):
        """Sets up test data."""
        self.show = Show.objects.create(
            name="Test Show name",
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
                "active": False,
            },
        )

from datetime import datetime

from django.utils.crypto import get_random_string
from django.test import TestCase
from rest_framework.test import APIRequestFactory

from ..models import Episode
from ..serializers import EpisodeSerializer
from apps.hosts.models import Host


class EpisodeModelTest(TestCase):
    """Tests Episode model."""

    def setUp(self):
        """Sets up test data."""
        self.video_id = get_random_string(length=11)

        self.episode = Episode.objects.create(
            title="Test Episode title",
            release_date=datetime.now().date(),
            video_id=self.video_id,
            link=f"https://www.youtube.com/watch?v={self.video_id}",
        )

    def test_model_str(self):
        """Tests model __str__."""
        self.assertEqual(str(self.episode), self.episode.title)


class EpisodeSerializerTest(TestCase):
    """Tests Episode serializer."""

    def setUp(self):
        """Sets up test data."""
        self.video_id = get_random_string(length=11)
        self.release_date = datetime.now().date()

        self.episode = Episode.objects.create(
            title="Test Episode title",
            release_date=self.release_date,
            video_id=self.video_id,
            link=f"https://www.youtube.com/watch?v={self.video_id}",
        )

        self.host = Host.objects.create(name="Test Host name")

        self.episode.hosts.add(self.host)

    def test_to_representation(self):
        """Tests custom to_representation()."""
        request_factory = APIRequestFactory()
        request = request_factory.post(
            "/api/episodes/?title=Test+Episode+title"
        )
        data = EpisodeSerializer(
            self.episode, context={"request": request}
        ).data
        self.assertEqual(
            data,
            {
                "title": "Test Episode title",
                "release_date": str(self.release_date),
                "hosts": ["Test Host name"],
                "guests": [],
                "video_id": self.video_id,
                "link": f"https://www.youtube.com/watch?v={self.video_id}",
                "short": False,
                "members_only": False,
            },
        )

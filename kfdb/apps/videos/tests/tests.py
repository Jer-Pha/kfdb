from datetime import datetime

from django.utils.crypto import get_random_string
from django.test import TestCase
from rest_framework.test import APIRequestFactory

from ..models import Video
from ..serializers import VideoSerializer
from apps.hosts.models import Host


class VideoModelTest(TestCase):
    """Tests Video model."""

    def setUp(self):
        """Sets up test data."""
        self.video_id = get_random_string(length=11)

        self.video = Video.objects.create(
            title="Test Video title",
            release_date=datetime.now().date(),
            video_id=self.video_id,
            link=f"https://www.youtube.com/watch?v={self.video_id}",
        )

    def test_model_str(self):
        """Tests model __str__."""
        self.assertEqual(str(self.video), self.video.title)


class VideoSerializerTest(TestCase):
    """Tests Video serializer."""

    def setUp(self):
        """Sets up test data."""
        self.video_id = get_random_string(length=11)
        self.release_date = datetime.now().date()

        self.video = Video.objects.create(
            title="Test Video title",
            release_date=self.release_date,
            video_id=self.video_id,
            link=f"https://www.youtube.com/watch?v={self.video_id}",
        )

        self.host = Host.objects.create(name="Test Host name")

        self.video.hosts.add(self.host)

    def test_to_representation(self):
        """Tests custom to_representation()."""
        request_factory = APIRequestFactory()
        request = request_factory.post("/api/videos/?title=Test+Video+title")
        data = VideoSerializer(self.video, context={"request": request}).data
        self.assertEqual(
            data,
            {
                "title": "Test Video title",
                "release_date": str(self.release_date),
                "hosts": [
                    {"type": "Host", "id": "1", "name": "Test Host name"}
                ],
                "video_id": self.video_id,
                "link": f"https://www.youtube.com/watch?v={self.video_id}",
            },
        )

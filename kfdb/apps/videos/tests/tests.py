from datetime import datetime

from django.utils.crypto import get_random_string
from django.test import RequestFactory, TestCase
from django.urls import reverse
from rest_framework.test import APIRequestFactory

from ..models import Video
from ..serializers import VideoSerializer
from ..views import AllVideosView
from apps.hosts.models import Host


class VideoModelTest(TestCase):
    """Tests Video model."""

    def setUp(self):
        """Sets up test data."""
        self.video_id = get_random_string(length=11)

        self.video = Video.objects.create(
            title="Test Video",
            release_date=datetime.now().date(),
            video_id=self.video_id,
            link=f"https://www.youtube.com/watch?v={self.video_id}",
        )
        self.short = Video.objects.create(
            title="Test Short",
            release_date=datetime.now().date(),
            video_id="ABCDE-FGHIJ",
            link=f"https://www.youtube.com/shorts/ABCDE-FGHIJ",
        )
        self.patreon = Video.objects.create(
            title="Test Video title",
            release_date=datetime.now().date(),
            video_id="1234567890",
            link=f"https://www.patreon.com/posts/1234567890",
        )

    def test_model_str(self):
        """Tests model __str__."""
        self.assertEqual(str(self.video), self.video.title)

    def test_model_properties(self):
        """Tests model properties."""
        self.assertEqual(self.video.embed_size, "w-full aspect-[16/9]")
        self.assertEqual(self.short.embed_size, "w-[270px] aspect-[9/16]")
        self.assertEqual(self.patreon.embed_size, "")


class VideoViewsTest(TestCase):
    """Tests Video views."""

    def test_new_page(self):
        """Tests view when `self.new_page == True`."""
        request = RequestFactory().get(reverse("videos_home"))
        view = AllVideosView.as_view()(request)
        context = view.context_data
        self.assertIn("videos", context)
        self.assertEqual(
            context["view"].template_name, "videos/videos-home.html"
        )

    def test_xhr_request(self):
        """Tests view when `self.new_page == False`."""
        request = RequestFactory(headers={"Hx-Request": True}).get(
            reverse("videos_home"),
        )
        view = AllVideosView.as_view()(request)
        context = view.context_data
        self.assertIn("videos", context)
        self.assertEqual(
            context["view"].template_name,
            "core/partials/get-video-results.html",
        )


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
                "hosts": [{"id": "1", "name": "Test Host name"}],
                "video_id": self.video_id,
                "link": f"https://www.youtube.com/watch?v={self.video_id}",
            },
        )

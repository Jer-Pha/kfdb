from datetime import datetime

from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.utils.crypto import get_random_string
from rest_framework.test import APIRequestFactory

from ..models import Video
from ..serializers import VideoSerializer
from ..views import (
    AllVideosChartsView,
    AllVideosView,
    VideoBlurbView,
    VideoDetailsView,
    VideoEmbedView,
)
from apps.channels.models import Channel
from apps.hosts.models import Host
from apps.shows.models import Show


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

    def setUp(self):
        """Sets up test data."""

        channel = Channel.objects.create(name="Test Channel")
        crew = Host.objects.create(name="Test Crew", kf_crew=True)
        part_timer = Host.objects.create(
            name="Test Part-Timer",
            part_timer=True,
        )
        guest = Host.objects.create(name="Test Guest")
        producer = Host.objects.create(name="Test Producer", kf_crew=True)

        for i in range(12):
            show = Show.objects.create(
                name=f"test show {i}",
            )
            video_id = f"012345678{i}"
            video = Video.objects.create(
                title=f"Test Video ({video_id})",
                release_date=f"2024-{str(i+1).zfill(2)}-01",
                show=show,
                channel=channel,
                producer=producer,
                video_id=video_id,
                blurb=get_random_string(length=32),
                link=f"https://www.youtube.com/watch?v={video_id}",
            )
            video.hosts.add(crew)
            if not i % 2:
                video.hosts.add(guest)
            if not i % 3 or not i % 5:
                video.hosts.add(part_timer)

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
            "videos/partials/get-video-results.html",
        )

    def test_video_details_view(self):
        """Tests VideoDetailsView()."""
        video_id = (
            Video.objects.values_list("video_id", flat=True).all().first()
        )
        request = RequestFactory().get(
            reverse("get_video_details") + f"?video_id={video_id}"
        )
        view = VideoDetailsView.as_view()(request)
        context = view.context_data
        self.assertIn("video", context)
        self.assertEqual(
            context["video"],
            (
                Video.objects.select_related("show", "producer", "channel")
                .prefetch_related("hosts")
                .get(video_id=video_id)
            ),
        )

    def test_video_blurb_view(self):
        """Tests VideoBlurbView()."""
        video_id = (
            Video.objects.values_list("video_id", flat=True).all().first()
        )
        request = RequestFactory().get(
            reverse("get_video_blurb") + f"?video_id={video_id}"
        )
        view = VideoBlurbView.as_view()(request)
        context = view.context_data
        self.assertIn("blurb", context)
        self.assertEqual(
            context["blurb"],
            Video.objects.values_list("blurb", flat=True).get(
                video_id=video_id
            ),
        )

    def test_video_embed_view(self):
        """Tests VideoEmbedView()."""
        video_id = (
            Video.objects.values_list("video_id", flat=True).all().first()
        )
        request = RequestFactory().get(
            reverse("get_video_embed") + f"?video_id={video_id}"
        )
        view = VideoEmbedView.as_view()(request)
        context = view.context_data
        self.assertIn("video", context)
        self.assertEqual(
            context["video"],
            Video.objects.only("link", "title", "video_id").get(
                video_id=video_id
            ),
        )

    def test_show_charts_view(self):
        """Tests AllVideosChartsView()."""
        self.maxDiff = None
        request = RequestFactory().get(reverse("videos_home"))
        view = AllVideosChartsView.as_view()(request)
        context = view.context_data
        self.assertEqual(
            context["doughnut_data"],
            {
                "labels": [f"test show {i}" for i in range(10)] + ["Other"],
                "datasets": [
                    {
                        "label": " Shows",
                        "data": ([1] * 10) + [2],
                        "borderWidth": 1,
                    },
                ],
            },
        )
        self.assertEqual(
            context["doughnut_fallback"],
            list(
                zip(
                    [f"test show {i}" for i in range(10)] + ["Other"],
                    ([1] * 10) + [2],
                )
            ),
        )
        self.assertEqual(
            context["bar_data"],
            {
                "labels": [
                    "Jan '24",
                    "Feb '24",
                    "Mar '24",
                    "Apr '24",
                    "May '24",
                    "Jun '24",
                    "Jul '24",
                    "Aug '24",
                    "Sep '24",
                    "Oct '24",
                    "Nov '24",
                    "Dec '24",
                ],
                "datasets": [
                    {
                        "label": " Video",
                        "data": [1] * 12,
                    },
                ],
            },
        )
        self.assertEqual(
            context["bar_fallback"],
            list(
                zip(
                    [
                        "Jan '24",
                        "Feb '24",
                        "Mar '24",
                        "Apr '24",
                        "May '24",
                        "Jun '24",
                        "Jul '24",
                        "Aug '24",
                        "Sep '24",
                        "Oct '24",
                        "Nov '24",
                        "Dec '24",
                    ],
                    [(1,)] * 12,
                )
            ),
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
                "hosts": [
                    {
                        "id": "1",
                        "name": "Test Host name",
                        "slug": "test-host-name",
                    }
                ],
                "video_id": self.video_id,
                "link": f"https://www.youtube.com/watch?v={self.video_id}",
            },
        )

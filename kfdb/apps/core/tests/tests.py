from datetime import datetime

from django.utils.crypto import get_random_string
from django.test import RequestFactory, TestCase
from django.urls import reverse

from apps.channels.models import Channel
from apps.hosts.models import Host
from apps.shows.models import Show
from apps.videos.models import Video
from apps.videos.views import AllVideosView


class CoreViewsTest(TestCase):
    """Tests Core views."""

    def setUp(self):
        """Sets up test data."""

        channel = Channel.objects.create(name="Test Channel")
        crew = Host.objects.create(name="Test Crew")
        part_timer = Host.objects.create(name="Test Part-Timer")
        guest = Host.objects.create(name="Test Guest")
        producer = Host.objects.create(name="Test Producer")
        show = Show.objects.create(name="Test Show")

        for i in range(60):
            video_id = get_random_string(length=11)
            video = Video.objects.create(
                title=f"Test Video ({video_id})",
                release_date=datetime.now().date(),
                show=show,
                channel=channel,
                producer=producer,
                video_id=video_id,
                link=f"https://www.youtube.com/watch?v={video_id}",
            )
            video.hosts.add(crew)
            if not i % 2:
                video.hosts.add(guest)
            if not i % 3 or not i % 5:
                video.hosts.add(part_timer)

    def test_get_videos(self):
        """Tests get_videos()."""
        tests = [
            {
                "params": (
                    "?page=1&sort=title&search=test%20video"
                    "&channel=test-channel&show=test-show&guest=test-guest"
                    "&producer=test-producer&part-timer=test-part-timer"
                    "&crew=test-crew&results=100"
                ),
                "page_range": None,
                "count": 14,
            },
            {
                "params": (
                    "?page=1&sort=title&search=test%20video"
                    "&channel=test-channel&show=test-show&guest=test-guest"
                    "&producer=test-producer&part-timer=test-part-timer"
                ),
                "page_range": None,
                "count": 14,
            },
            {
                "params": "?page=1&sort=-title&results=10",
                "page_range": [1, 2, 3, "...", 6],
                "count": 10,
            },
            {
                "params": "?page=2&results=25",
                "page_range": range(1, 4),
                "count": 25,
            },
            {
                "params": "?page=3&results=10",
                "page_range": [1, "...", 2, 3, 4, "...", 6],
                "count": 10,
            },
            {
                "params": "?page=6&results=10",
                "page_range": [1, "...", 4, 5, 6],
                "count": 10,
            },
        ]

        for test in tests:
            request = RequestFactory().get(
                reverse("videos_home") + test["params"]
            )
            view = AllVideosView.as_view()(request)
            context = view.context_data
            self.assertIn("videos", context)
            self.assertEqual(context["view"].page_range, test["page_range"])
            self.assertEqual(len(context["videos"]), test["count"])

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

        for i in range(10):
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

    def test_video_filter(self):
        """Tests build_filter()."""
        request = RequestFactory().get(
            reverse("videos_home")
            + (
                "?page=1&sort=release_date&search=test%20video"
                "&channel=test-channel&show=test-show&guest=test-guest"
                "&producer=test-producer&part-timer=test-part-timer"
                "&crew=test-crew&results=100"
            )
        )
        view = AllVideosView()
        view.setup(request)
        view.get(request)
        context = view.get_context_data()
        self.assertIn("videos", context)
        self.assertEqual(len(context["videos"]), 2)

from datetime import datetime

from django.utils.crypto import get_random_string
from django.test import RequestFactory, TestCase
from django.urls import reverse

from ..models import ChannelEdit, HostEdit, ShowEdit, VideoEdit
from ..views import EditChannelView, EditHostView, EditShowView, EditVideoView
from apps.channels.models import Channel
from apps.hosts.models import Host
from apps.shows.models import Show
from apps.videos.models import Video


class EditViewsTest(TestCase):
    """Tests Edit views."""

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
        show = Show.objects.create(name="Test Show")

        video_id = get_random_string(length=11)
        video = Video.objects.create(
            title=f"Test Video ({video_id})",
            release_date=datetime.now().date(),
            show=show,
            channel=channel,
            producer=producer,
            video_id=video_id,
            blurb=get_random_string(length=32),
            link=f"https://www.youtube.com/watch?v={video_id}",
        )
        video.hosts.add(crew, guest, part_timer)

    def test_edit_channel_view(self):
        """Tests EditChannelView() GET and POST requests."""
        channel_id = 1
        get_request = RequestFactory().get(
            reverse("edit_channel") + f"?channel={channel_id}"
        )
        get_view = EditChannelView.as_view()(get_request)
        get_context = get_view.context_data
        self.assertIn("obj", get_context)
        self.assertEqual(
            get_context["obj"],
            Channel.objects.values_list("id", "name").get(id=channel_id),
        )

        post_request = RequestFactory().post(
            reverse("edit_channel"),
            data={
                "id": 1,
                "topic": "",
                "description": "test description",
                "username": "",
            },
        )
        EditChannelView.as_view()(post_request)
        self.assertTrue(
            ChannelEdit.objects.filter(
                channel=Channel.objects.get(id=1),
            ).exists()
        )

    def test_edit_host_view(self):
        """Tests EditHostView() GET and POST requests."""
        host_id = 1
        get_request = RequestFactory().get(
            reverse("edit_host") + f"?host={host_id}"
        )
        get_view = EditHostView.as_view()(get_request)
        get_context = get_view.context_data
        self.assertIn("obj", get_context)
        self.assertEqual(
            get_context["obj"],
            Host.objects.values_list("id", "name").get(id=host_id),
        )

        post_request = RequestFactory().post(
            reverse("edit_host"),
            data={
                "id": 1,
                "topic": "",
                "description": "test description",
                "username": "",
            },
        )
        EditHostView.as_view()(post_request)
        self.assertTrue(
            HostEdit.objects.filter(
                host=Host.objects.get(id=1),
            ).exists()
        )

    def test_edit_show_view(self):
        """Tests EditShowView() GET and POST requests."""
        show_id = 1
        get_request = RequestFactory().get(
            reverse("edit_show") + f"?show={show_id}"
        )
        get_view = EditShowView.as_view()(get_request)
        get_context = get_view.context_data
        self.assertIn("obj", get_context)
        self.assertEqual(
            get_context["obj"],
            Show.objects.values_list("id", "name").get(id=show_id),
        )

        post_request = RequestFactory().post(
            reverse("edit_show"),
            data={
                "id": 1,
                "topic": "",
                "description": "test description",
                "username": "",
            },
        )
        EditShowView.as_view()(post_request)
        self.assertTrue(
            ShowEdit.objects.filter(
                description="test description",
                show=Show.objects.get(id=1),
            ).exists()
        )

    def test_edit_video_view(self):
        """Tests EditVideoView() GET and POST requests."""
        video_id = 1
        get_request = RequestFactory().get(
            reverse("edit_video") + f"?video={video_id}"
        )
        get_view = EditVideoView.as_view()(get_request)
        get_context = get_view.context_data
        self.assertIn("obj", get_context)
        self.assertEqual(
            get_context["obj"],
            Video.objects.values_list("id", "title").get(id=video_id),
        )
        self.assertEqual(
            get_context["view"].template_name,
            "edits/partials/edit-video-modal.html",
        )

        post_request = RequestFactory().post(
            reverse("edit_video"),
            data={
                "id": 1,
                "topic": "test topic",
                "description": "test      description",
                "username": "        test username          ",
            },
        )
        post_view = EditVideoView.as_view()(post_request)
        post_context = post_view.context_data
        self.assertEqual(post_view.status_code, 201)
        self.assertIn("message", post_context)
        self.assertEqual(
            post_context["message"],
            "Thank you for your suggestion!",
        )
        self.assertTrue(
            VideoEdit.objects.filter(
                topic="test topic",
                description="test description",
                username="test username",
                video=Video.objects.get(id=1),
            ).exists()
        )

        post_request_error = RequestFactory().post(
            reverse("edit_video"),
            data={
                "id": 100,
                "topic": "test topic",
                "description": "test description",
                "username": "test username",
            },
        )
        post_view_error = EditVideoView.as_view()(post_request_error)
        post_context_error = post_view_error.context_data
        self.assertEqual(post_view_error.status_code, 202)
        self.assertIn("message", post_context_error)
        self.assertIn(
            "Oops, something went wrong!",
            post_context_error["message"],
        )
        self.assertFalse(
            VideoEdit.objects.filter(
                topic="test topic",
                description="test description",
                username="test username",
                video=Video.objects.filter(id=100).first(),
            ).exists()
        )

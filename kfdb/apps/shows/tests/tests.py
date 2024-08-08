from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory, TestCase
from django.urls import reverse
from rest_framework.test import APIRequestFactory

from ..models import Show
from ..serializers import ShowSerializer
from ..views import ShowChartsView, ShowPageView, ShowsHomeView
from apps.channels.models import Channel
from apps.hosts.models import Host
from apps.videos.models import Video

# Bytes representing a valid 1-pixel PNG
ONE_PIXEL_PNG_BYTES = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00"
    b"\x01\x08\x04\x00\x00\x00\xb5\x1c\x0c\x02\x00\x00\x00\x0bIDATx"
    b"\x9cc\xfa\xcf\x00\x00\x02\x07\x01\x02\x9a\x1c1q\x00\x00\x00"
    b"\x00IEND\xaeB`\x82"
)


class ShowModelTest(TestCase):
    """Tests Show model."""

    def setUp(self):
        """Sets up test data."""
        self.show = Show.objects.create(
            name="Test Show name",
            image=SimpleUploadedFile(
                name="test.png",
                content=ONE_PIXEL_PNG_BYTES,
                content_type="image/png",
            ),
        )

    def test_model_str(self):
        """Tests model __str__."""
        self.assertEqual(str(self.show), self.show.name)


class ShowViewsTest(TestCase):
    """Tests Show views."""

    def setUp(self):
        """Sets up test data."""
        show_1 = Show.objects.create(
            name="Test Show",
            slug="test",
            image=SimpleUploadedFile(
                name="test.png",
                content=ONE_PIXEL_PNG_BYTES,
                content_type="image/png",
            ),
            image_xs=SimpleUploadedFile(
                name="test_xs.png",
                content=ONE_PIXEL_PNG_BYTES,
                content_type="image/png",
            ),
            active=True,
            blurb="Test blurb.",
        )

        Channel.objects.bulk_create(
            (
                Channel(name="KF Prime", slug="prime"),
                Channel(name="KF Games", slug="games"),
                Channel(name="KF Membership", slug="members"),
            )
        )

        channel_prime = Channel.objects.get(id=1)
        producer_1 = Host.objects.create(
            name="test producer 1",
            kf_crew=True,
        )
        producer_2 = Host.objects.create(
            name="test producer 2",
            kf_crew=True,
        )

        for i in range(12):
            Host.objects.create(
                name=f"test host {i}",
                kf_crew=(True if i < 2 else False),
                part_timer=(True if i > 3 else False),
            )
            video = Video.objects.create(
                title=f"test video {i}",
                release_date=f"2024-{str(i+1).zfill(2)}-01",
                show=show_1,
                channel=channel_prime,
                video_id=f"012345678{i}",
                producer=(producer_1 if not i % 2 else None),
            )
            hosts = Host.objects.filter(id__gt=2, id__lte=(i + 3))
            video.hosts.add(*hosts)
            if i % 2:
                video.hosts.add(producer_1)
            elif i == 10:
                video.hosts.add(producer_2)
            if i == 11:
                video.producer = producer_2
                video.save()

        show_1.channels.add(*Channel.objects.all())

        show_2 = Show.objects.create(
            name="test show 2",
        )
        for i in range(12):
            video = Video.objects.create(
                title=f"test video {i}",
                release_date=f"2024-{str(i+1).zfill(2)}-01",
                show=show_2,
                channel=(
                    channel_prime if i < 9 else Channel.objects.get(id=2)
                ),
                video_id=f"112345678{i}",
                producer=(producer_1 if i % 2 else None),
            )
            hosts = Host.objects.filter(id__gt=2, id__lte=(i + 3))
            video.hosts.add(*hosts)

    def test_new_page(self):
        """Tests view when `self.new_page == True`."""
        request = RequestFactory().get(
            reverse("show_page", kwargs={"show": "test"})
        )
        view = ShowPageView.as_view()(request, show="test")
        context = view.context_data
        self.assertIn("videos", context)
        self.assertIn("filter_param", context)
        self.assertEqual(context["view"].template_name, "shows/show-page.html")

        request_2 = RequestFactory().get(
            reverse("show_page", kwargs={"show": "test"}) + "?channel=prime"
        )
        view_2 = ShowPageView.as_view()(request_2, show="test")
        self.assertEqual(
            view_2.context_data["filter_param"], f"s=1&channel=prime"
        )

    def test_xhr_request(self):
        """Tests view when `self.new_page == False`."""
        request = RequestFactory(headers={"Hx-Request": True}).get(
            reverse("show_page", kwargs={"show": "test"}),
        )
        view = ShowPageView.as_view()(request, show="test")
        context = view.context_data
        self.assertIn("videos", context)
        self.assertNotIn("filter_param", context)
        self.assertEqual(
            context["view"].template_name,
            "videos/partials/get-video-results.html",
        )

    def test_all_shows_view(self):
        """Tests ShowsHomeView()."""
        request = RequestFactory().get(reverse("shows_home"))
        view = ShowsHomeView.as_view()(request)
        context = view.context_data
        self.assertIn("games", context)
        self.assertIn("prime", context)
        self.assertIn("members", context)
        self.assertEqual(len(context["games"]), 1)
        self.assertEqual(len(context["prime"]), 1)
        self.assertEqual(len(context["members"]), 1)

    def test_show_charts_view(self):
        """Tests ShowChartsView()."""
        self.maxDiff = None
        request_1 = RequestFactory().get(
            reverse("show_charts") + "?show=1&channel=prime"
        )
        view_1 = ShowChartsView.as_view()(request_1)
        context_1 = view_1.context_data
        self.assertEqual(
            context_1["doughnut_data"],
            {
                "labels": (
                    [f"test host {i}" for i in range(6)]
                    + ["test producer 1"]
                    + [f"test host {i}" for i in range(6, 8)]
                    + ["test host 8"]
                    + ["Other"]
                ),
                "datasets": [
                    {
                        "label": " Appearances",
                        "data": (
                            [i for i in range(12, 6, -1)]
                            + [12]
                            + [i for i in range(6, 3, -1)]
                            + [8]
                        ),
                        "borderWidth": 1,
                    },
                ],
            },
        )
        self.assertEqual(
            context_1["doughnut_fallback"],
            list(
                zip(
                    (
                        [f"test host {i}" for i in range(6)]
                        + ["test producer 1"]
                        + [f"test host {i}" for i in range(6, 8)]
                        + ["test host 8"]
                        + ["Other"]
                    ),
                    (
                        [i for i in range(12, 6, -1)]
                        + [12]
                        + [i for i in range(6, 3, -1)]
                        + [8]
                    ),
                )
            ),
        )

        request_2 = RequestFactory().get(reverse("show_charts") + "?show=1")
        view_2 = ShowChartsView.as_view()(request_2)
        context_2 = view_2.context_data
        self.assertEqual(
            context_2["bar_data"],
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
            context_2["bar_fallback"],
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

        request_3 = RequestFactory().get(
            reverse("show_charts") + "?show=1&channel=members"
        )
        view_3 = ShowChartsView.as_view()(request_3)
        context_3 = view_3.context_data
        self.assertNotIn("doughnut_data", context_3)
        self.assertNotIn("doughnut_fallback", context_3)
        self.assertNotIn("doughnut_title", context_3)
        self.assertIn("bar_data", context_3)
        self.assertIn("bar_fallback", context_3)
        self.assertIn("bar_title", context_3)

        request_4 = RequestFactory().get(reverse("show_charts") + "?show=2")
        view_4 = ShowChartsView.as_view()(request_4)
        context_4 = view_4.context_data
        self.assertIn("bar_data", context_4)

        request_5 = RequestFactory().get(
            reverse("show_charts") + "?show=2&channel=prime"
        )
        view_5 = ShowChartsView.as_view()(request_5)
        context_5 = view_5.context_data
        self.assertIn("bar_data", context_5)


class ShowSerializerTest(TestCase):
    """Tests Show serializer."""

    def setUp(self):
        """Sets up test data."""
        self.show = Show.objects.create(
            name="Test Show name",
            active=True,
            image_xs=SimpleUploadedFile(
                name="test.png",
                content=ONE_PIXEL_PNG_BYTES,
                content_type="image/png",
            ),
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
                "slug": "test-show-name",
                "active": True,
            },
        )

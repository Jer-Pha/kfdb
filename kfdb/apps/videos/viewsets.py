from drf_spectacular.utils import extend_schema
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import Video
from .serializers import VideoSerializer


@method_decorator(
    cache_page(60 * 5, key_prefix="API_videos"),
    name="dispatch",
)
@extend_schema(description="Videos are the core item of the database.")
class VideoViewSet(ReadOnlyModelViewSet):
    queryset = (
        Video.objects.select_related("show", "channel")
        .prefetch_related("hosts")
        .all()
    )
    serializer_class = VideoSerializer
    search_fields = ("title", "blurb")
    filterset_fields = {
        "id": ["exact"],
        "video_id": ["exact"],
        "release_date": ["exact", "gt", "gte", "lt", "lte"],
        "hosts": ["exact"],
        "hosts__id": ["exact", "in"],
        "hosts__slug": ["exact"],
        "channel": ["exact"],
        "channel__id": ["exact"],
        "channel__slug": ["exact"],
        "show": ["exact"],
        "show__id": ["exact"],
        "show__slug": ["exact"],
        "producer": ["exact"],
        "producer__id": ["exact"],
        "producer__slug": ["exact"],
    }

from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import Video
from .serializers import VideoSerializer


class VideoViewSet(ReadOnlyModelViewSet):
    queryset = (
        Video.objects.select_related("show", "channel")
        .prefetch_related("hosts")
        .all()
    )
    serializer_class = VideoSerializer
    search_fields = (
        "title",
        "blurb",
    )

    filterset_fields = (
        "title",
        "slug",
        "blurb",
        "hosts",
        "producer",
    )

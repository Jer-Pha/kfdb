from rest_framework.viewsets import ModelViewSet

from .models import Video
from .serializers import VideoSerializer


class VideoViewSet(ModelViewSet):
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
        "blurb",
        "hosts",
        "guests",
        "producer",
        "short",
        "members_only",
    )

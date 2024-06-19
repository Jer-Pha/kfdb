from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import Channel
from .serializers import ChannelSerializer


class ChannelViewSet(ReadOnlyModelViewSet):
    queryset = Channel.objects.all()
    serializer_class = ChannelSerializer
    search_fields = (
        "name",
        "blurb",
    )

    filterset_fields = ("name", "slug")

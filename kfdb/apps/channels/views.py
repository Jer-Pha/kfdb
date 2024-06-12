from rest_framework.viewsets import ModelViewSet

from .models import Channel
from .serializers import ChannelSerializer


class ChannelViewSet(ModelViewSet):
    queryset = Channel.objects.all()
    serializer_class = ChannelSerializer
    search_fields = (
        "name",
        "blurb",
    )

    filterset_fields = ("name",)

from drf_spectacular.utils import extend_schema
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import Channel
from .serializers import ChannelSerializer


@method_decorator(
    cache_page(60 * 5, key_prefix="API_channels"),
    name="dispatch",
)
@extend_schema(
    description=(
        "Channels are the most basic way to filter Kinda Funny"
        " content. The main channels are KF Games and KF Prime."
    )
)
class ChannelViewSet(ReadOnlyModelViewSet):
    queryset = Channel.objects.all()
    serializer_class = ChannelSerializer
    filterset_fields = ("id", "name", "slug")

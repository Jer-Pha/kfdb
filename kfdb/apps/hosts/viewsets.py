from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import Host
from .serializers import HostSerializer


class HostViewSet(ReadOnlyModelViewSet):
    queryset = Host.objects.all()
    serializer_class = HostSerializer
    search_fields = (
        "name",
        "nicknames",
        "blurb",
    )

    filterset_fields = (
        "name",
        "slug",
        "kf_crew",
        "part_timer",
    )

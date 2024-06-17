from rest_framework.viewsets import ModelViewSet

from .models import Host
from .serializers import HostSerializer


class HostViewSet(ModelViewSet):
    queryset = Host.objects.all()
    serializer_class = HostSerializer
    search_fields = (
        "name",
        "nicknames",
        "blurb",
    )

    filterset_fields = (
        "name",
        "kf_crew",
        "part_timer",
    )

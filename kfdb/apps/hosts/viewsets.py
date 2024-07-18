from drf_spectacular.utils import extend_schema

from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import Host
from .serializers import HostSerializer


@extend_schema(
    description="Hosts include the KF Crew, Part-Timers, and Guests."
)
class HostViewSet(ReadOnlyModelViewSet):
    queryset = Host.objects.all()
    serializer_class = HostSerializer
    search_fields = ("name", "slug")
    filterset_fields = ("id", "name", "slug", "kf_crew", "part_timer")

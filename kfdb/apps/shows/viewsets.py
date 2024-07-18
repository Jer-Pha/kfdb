from drf_spectacular.utils import extend_schema

from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import Show
from .serializers import ShowSerializer


@extend_schema(
    description="Shows are how videos are categorized in the database."
)
class ShowViewSet(ReadOnlyModelViewSet):
    queryset = Show.objects.all()
    serializer_class = ShowSerializer
    filterset_fields = ("id", "name", "slug", "active", "channels")

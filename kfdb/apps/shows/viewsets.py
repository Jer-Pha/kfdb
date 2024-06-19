from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import Show
from .serializers import ShowSerializer


class ShowViewSet(ReadOnlyModelViewSet):
    queryset = Show.objects.all()
    serializer_class = ShowSerializer
    search_fields = (
        "name",
        "blurb",
    )

    filterset_fields = (
        "name",
        "slug",
        "active",
    )

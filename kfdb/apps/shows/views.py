from rest_framework.viewsets import ModelViewSet

from .models import Show
from .serializers import ShowSerializer


class ShowViewSet(ModelViewSet):
    queryset = Show.objects.all()
    serializer_class = ShowSerializer
    search_fields = (
        "name",
        "blurb",
    )

    filterset_fields = (
        "name",
        "active",
    )

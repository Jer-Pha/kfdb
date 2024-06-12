from rest_framework.viewsets import ModelViewSet

from .models import Episode
from .serializers import EpisodeSerializer


class EpisodeViewSet(ModelViewSet):
    queryset = (
        Episode.objects.select_related("show", "channel")
        .prefetch_related("hosts")
        .all()
    )
    serializer_class = EpisodeSerializer
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

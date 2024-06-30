from django.db.models import Prefetch, Q

from apps.channels.models import Channel
from apps.hosts.models import Host
from apps.shows.models import Show
from apps.videos.models import Video


class Filter:
    def __init__(self, channel_id=0, show_id=0, host_id=0):
        self.channel_id = channel_id
        self.show_id = show_id
        self.host_id = host_id
        self.context = {}

    def build_channels(self):
        if self.show_id:
            response = Video.objects.select_related("channel").filter(
                show=self.show_id
            )
        elif self.host_id:
            response = (
                Video.objects.select_related("channel")
                .prefetch_related(
                    Prefetch(
                        "hosts",
                        queryset=Host.objects.filter(id=self.host_id).only(
                            "id"
                        ),
                    )
                )
                .filter(hosts=self.host_id)
            )
        else:
            return list(
                Channel.objects.all()
                .values_list("slug", "name")
                .order_by("name")
            )
        return list(
            response.distinct()
            .values_list("channel__slug", "channel__name")
            .order_by("channel__name")
        )

    def build_shows(self, active):
        if self.channel_id:
            response = Video.objects.select_related("show").filter(
                channel=self.channel_id, show__active=active
            )
        elif self.host_id:
            response = (
                Video.objects.select_related("show")
                .prefetch_related(
                    Prefetch(
                        "hosts",
                        queryset=Host.objects.filter(id=self.host_id).only(
                            "id"
                        ),
                    )
                )
                .filter(show__active=active, hosts=self.host_id)
            )
        else:
            return list(
                Show.objects.filter(active=active)
                .values_list("slug", "name")
                .order_by("name")
            )
        return list(
            response.distinct()
            .values_list("show__slug", "show__name")
            .order_by("show__name")
        )

    def build_hosts(self, crew, pt):
        if self.channel_id:
            videos = Video.objects.filter(channel=self.channel_id).values_list(
                "id", flat=True
            )
            response = Host.objects.filter(
                video_host__in=videos, kf_crew=crew, part_timer=pt
            )
        elif self.show_id:
            videos = Video.objects.filter(show=self.show_id).values_list(
                "id", flat=True
            )
            response = Host.objects.filter(
                video_host__in=videos, kf_crew=crew, part_timer=pt
            )
        elif self.host_id:
            videos = Video.objects.filter(hosts=self.host_id).values_list(
                "id", flat=True
            )
            response = Host.objects.filter(
                video_host__in=videos, kf_crew=crew, part_timer=pt
            )
        else:
            response = Host.objects.filter(kf_crew=crew, part_timer=pt)
        return list(
            response.exclude(id=self.host_id)
            .distinct()
            .values_list("slug", "name")
            .order_by("name")
        )

    def build_producers(self):
        if self.channel_id:
            response = Video.objects.select_related(
                "producer", "channel"
            ).filter(channel=self.channel_id, producer__isnull=False)
        elif self.show_id:
            response = Video.objects.select_related("producer", "show").filter(
                show=self.show_id, producer__isnull=False
            )
        elif self.host_id:
            response = (
                Video.objects.select_related("producer")
                .prefetch_related(
                    Prefetch(
                        "hosts",
                        queryset=Host.objects.filter(id=self.host_id).only(
                            'id"'
                        ),
                    )
                )
                .filter(
                    Q(hosts=self.host_id, producer__isnull=False)
                    | Q(producer=self.host_id)
                )
            )
        else:
            response = Video.objects.select_related("producer").filter(
                producer__isnull=False
            )

        return list(
            response.distinct()
            .values_list("producer__slug", "producer__name")
            .order_by("producer__name")
        )

    def add_channels(self):
        self.context["channels"] = self.build_channels()

    def add_shows(self):
        self.context["shows_active"] = self.build_shows(True)
        self.context["shows_inactive"] = self.build_shows(False)

    def add_hosts(self):
        self.context["hosts_crew"] = self.build_hosts(True, False)
        self.context["hosts_part_timers"] = self.build_hosts(False, True)
        self.context["hosts_guests"] = self.build_hosts(False, False)
        self.context["hosts_producers"] = self.build_producers()

    def channel_filter(self):
        self.add_shows()
        self.add_hosts()
        return self.context

    def show_filter(self):
        self.add_channels()
        self.add_hosts()
        return self.context

    def host_filter(self):
        self.add_channels()
        self.add_shows()
        self.add_hosts()
        return self.context

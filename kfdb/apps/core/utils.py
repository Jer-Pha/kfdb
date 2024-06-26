from apps.hosts.models import Host
from apps.shows.models import Show
from apps.videos.models import Video


class Filter:
    def __init__(self, channel_id=None):
        self.channel_id = channel_id
        self.context = {}

    def build_shows(self, channel, active):
        if channel:
            return list(
                Video.objects.select_related("show")
                .filter(channel=channel, show__active=active)
                .distinct()
                .values_list("show__slug", "show__name")
                .order_by("show__name")
            )
        return list(
            Show.objects.filter(active=active)
            .values_list("slug", "name")
            .order_by("name")
        )

    def build_hosts(self, crew, pt):
        return list(
            Host.objects.filter(kf_crew=crew, part_timer=pt)
            .values("slug", "name")
            .order_by("name")
        )

    def add_channels(self):
        self.context.update(
            {
                "channels": ("kf", "kfg"),
            }
        )

    def add_shows(self):
        self.context.update(
            {
                "shows_active": self.build_shows(self.channel_id, True),
                "shows_inactive": self.build_shows(self.channel_id, False),
            }
        )

    def add_hosts(self):
        self.context.update(
            {
                "hosts_crew": self.build_hosts(True, False),
                "hosts_part_timers": self.build_hosts(False, True),
                "hosts_guests": self.build_hosts(False, False),
            }
        )

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
        return self.context

from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from apps.channels.models import Channel
from apps.hosts.models import Host
from apps.shows.models import Show


class CoreViewSitemap(Sitemap):
    changefreq = "weekly"
    protocol = "https"
    priority = 1.0

    def items(self):
        return (
            "hero",
            "index",
            "api_docs",
        )

    def location(self, item):
        return reverse(item)


class StaticViewSitemap(Sitemap):
    changefreq = "yearly"
    protocol = "https"
    priority = 0.2

    def items(self):
        return (
            "about",
            "support",
            "hosts_crew",
            "hosts_part_timers",
            "hosts_guests",
            "channels_home",
            "privacy_policy",
        )

    def location(self, item):
        return reverse(item)


class PriorityStaticViewSitemap(Sitemap):
    changefreq = "weekly"
    protocol = "https"
    priority = 0.9

    def items(self):
        return (
            "videos_home",
            "hosts_home",
            "shows_home",
        )

    def location(self, item):
        return reverse(item)


class ChannelSitemap(Sitemap):
    changefreq = "weekly"
    protocol = "https"
    priority = 0.4

    def items(self):
        return Channel.objects.all().values("slug").order_by("pk")

    def location(self, channel):
        return f"/channels/{channel['slug']}/"


class ShowSitemap(Sitemap):
    changefreq = "weekly"
    protocol = "https"
    priority = 0.6

    def items(self):
        return Show.objects.all().values("slug").order_by("pk")

    def location(self, show):
        return f"/shows/{show['slug']}/"


class HostSitemap(Sitemap):
    changefreq = "weekly"
    protocol = "https"
    priority = 0.8

    def items(self):
        return (
            Host.objects.all()
            .only("slug", "kf_crew", "part_timer")
            .order_by("-kf_crew", "-part_timer", "name")
        )

    def location(self, host):
        return f"/hosts/{host.url_type}/{host.slug}/"

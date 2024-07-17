from copy import deepcopy

from rest_framework_json_api import serializers
from rest_framework_json_api.relations import ResourceRelatedField
from rest_framework_json_api.utils import get_resource_type_from_instance

from .models import Video
from apps.channels.models import Channel
from apps.hosts.models import Host
from apps.shows.models import Show


class StringResourceRelatedField(ResourceRelatedField):
    def to_representation(self, value):
        """Add `name` field to API `relationships` data."""
        pk = self.get_resource_id(value)
        resource_type = self.get_resource_type_from_included_serializer()
        if resource_type is None or not self._skip_polymorphic_optimization:
            resource_type = get_resource_type_from_instance(value)
        return {"type": resource_type, "id": str(pk), "name": str(value)}


class VideoSerializer(serializers.ModelSerializer):
    channel = StringResourceRelatedField(queryset=Channel.objects)
    hosts = StringResourceRelatedField(queryset=Host.objects, many=True)
    producer = StringResourceRelatedField(queryset=Host.objects)
    show = StringResourceRelatedField(queryset=Show.objects)

    class Meta:
        model = Video
        fields = [
            "title",
            "release_date",
            "show",
            "channel",
            "hosts",
            "producer",
            "video_id",
            "link",
            "blurb",
        ]

    def to_representation(self, instance):
        """Remove falsey values from API results."""
        obj = super().to_representation(instance)
        non_null = deepcopy(obj)
        for key in obj.keys():
            if not obj[key]:
                non_null.pop(key)
        return non_null

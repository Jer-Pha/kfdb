from copy import deepcopy

from rest_framework_json_api import serializers

from .models import Channel


class ChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Channel
        fields = [
            "name",
            "slug",
            "blurb",
        ]

    def to_representation(self, instance):
        """Remove falsey values from API results"""
        obj = super().to_representation(instance)
        non_null = deepcopy(obj)
        for key in obj.keys():
            if not obj[key]:
                non_null.pop(key)
        return non_null

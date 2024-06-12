from copy import deepcopy

from rest_framework import serializers

from .models import Channel


class ChannelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Channel
        fields = [
            # "id",
            "name",
            "blurb",
        ]

    def to_representation(self, instance):
        obj = super().to_representation(instance)
        non_null = deepcopy(obj)
        for key in obj.keys():
            if obj[key] is None:
                non_null.pop(key)
        return non_null

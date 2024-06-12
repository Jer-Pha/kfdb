from copy import deepcopy

from rest_framework import serializers

from .models import Episode


class CustomPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    def to_representation(self, value):
        return str(value)


class EpisodeSerializer(serializers.ModelSerializer):
    channel = serializers.StringRelatedField()
    guests = serializers.StringRelatedField(many=True)
    hosts = serializers.StringRelatedField(many=True)
    producer = serializers.StringRelatedField()
    show = serializers.StringRelatedField()

    class Meta:
        model = Episode
        fields = [
            "title",
            "release_date",
            "show",
            "channel",
            "hosts",
            "guests",
            "producer",
            "video_id",
            "link",
            "blurb",
            "short",
            "members_only",
        ]

    def to_representation(self, instance):
        obj = super().to_representation(instance)
        non_null = deepcopy(obj)
        for key in obj.keys():
            if obj[key] is None:
                non_null.pop(key)
        return non_null

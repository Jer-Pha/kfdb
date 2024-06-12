from copy import deepcopy

from rest_framework import serializers

from .models import Host


class HostSerializer(serializers.ModelSerializer):

    class Meta:
        model = Host
        fields = [
            "name",
            "nicknames",
            "kf_crew",
            "part_timer",
            "socials",
            "birthday",
            "blurb",
        ]

    def to_representation(self, instance):
        obj = super().to_representation(instance)
        non_null = deepcopy(obj)
        for key in obj.keys():
            if obj[key] is None:
                non_null.pop(key)
        return non_null

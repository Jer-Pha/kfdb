from copy import deepcopy

from rest_framework_json_api import serializers

from .models import Host


class HostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Host
        fields = [
            "name",
            "slug",
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
            if not obj[key]:
                non_null.pop(key)
        return non_null

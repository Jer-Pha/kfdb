from copy import deepcopy

from rest_framework import serializers

from .models import Show


class ShowSerializer(serializers.ModelSerializer):

    class Meta:
        model = Show
        fields = [
            # "id",
            "name",
            "active",
            "blurb",
        ]

    def to_representation(self, instance):
        obj = super().to_representation(instance)
        non_null = deepcopy(obj)
        for key in obj.keys():
            if obj[key] is None:
                non_null.pop(key)
        return non_null

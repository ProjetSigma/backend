from rest_framework import serializers

from sigma_core.models.group import Group


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group

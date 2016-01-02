from rest_framework import serializers

from sigma_core.models.group import Group


class BasicGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group


class GroupSerializer(BasicGroupSerializer):
    class Meta:
        model = Group

    memberships = serializers.PrimaryKeyRelatedField(read_only=True, many=True)

from rest_framework import serializers

from sigma_core.models.group import Group


class BasicGroupSerializer(serializers.ModelSerializer):
    """
    Serialize a Group without its relations with users.
    """
    class Meta:
        model = Group


class GroupSerializer(BasicGroupSerializer):
    """
    Serialize a Group and the related memberships.
    """
    class Meta:
        model = Group

    subgroups = serializers.PrimaryKeyRelatedField(read_only=True, many=True)
    memberships = serializers.PrimaryKeyRelatedField(read_only=True, many=True)

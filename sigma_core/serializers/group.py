from rest_framework import serializers

from sigma_core.models.group import Group


class GroupSerializer(serializers.ModelSerializer):
    """
    Serialize a Group without its relations with users.
    """
    class Meta:
        model = Group

    #members_count = serializers.IntegerField(read_only=True)

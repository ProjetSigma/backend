from rest_framework import serializers

from sigma_core.models.group import Group


class GroupSerializer(serializers.ModelSerializer):
    """
    Serialize a Group without its relations with users.
    """
    class Meta:
        model = Group
        exclude = ('resp_group', )

    resp_group_id = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all(), source='resp_group')
    members_count = serializers.IntegerField(read_only=True)

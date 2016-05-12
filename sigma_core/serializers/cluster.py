from rest_framework import serializers

from sigma_core.models.cluster import Cluster
from sigma_core.serializers.group import GroupSerializer

class BasicClusterSerializer(serializers.ModelSerializer):
    """
    Serialize Cluster model without memberships.
    """
    class Meta:
        model = Cluster
        exclude = (
            'req_rank_invite',
            'req_rank_kick',
            'req_rank_accept_join_requests',
            'req_rank_promote',
            'req_rank_demote',
            'req_rank_modify_group_infos',
            'default_member_rank',
            'is_protected',
            'is_private',
        )


class ClusterSerializer(BasicClusterSerializer):
    """
    Serialize Cluster model with memberships.
    """
    class Meta(BasicClusterSerializer.Meta):
        pass

    users_ids = serializers.PrimaryKeyRelatedField(read_only=True, many=True, source='users')

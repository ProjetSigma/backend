from rest_framework import serializers

from sigma_core.models.cluster import Cluster
from sigma_core.serializers.group import GroupSerializer

class BasicClusterSerializer(serializers.ModelSerializer):
    """
    Serialize Cluster model without memberships.
    """
    class Meta:
        model = Cluster
        exclude = ('resp_group',
            'req_rank_invite',
            'req_rank_kick',
            'req_rank_accept_join_requests',
            'req_rank_promote',
            'req_rank_demote',
            'req_rank_modify_group_infos',
            'default_member_rank',
            'protected',
            'private')


from sigma_core.serializers.user import BasicUserWithPermsSerializer
class ClusterSerializer(BasicClusterSerializer):
    """
    Serialize Cluster model with memberships.
    """
    class Meta(BasicClusterSerializer.Meta):
        pass

    users = BasicUserWithPermsSerializer(read_only=True, many=True)

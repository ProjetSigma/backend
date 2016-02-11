from rest_framework import serializers

from sigma_core.models.cluster import Cluster


class BasicClusterSerializer(serializers.ModelSerializer):
    """
    Serialize Cluster model without memberships.
    """
    class Meta:
        model = Cluster
        exclude = ('resp_cluster', )


from sigma_core.serializers.user import BasicUserWithPermsSerializer

class ClusterSerializer(BasicClusterSerializer):
    """
    Serialize Cluster model with memberships.
    """
    class Meta:
        model = Cluster
        exclude = ('resp_cluster', )

    users = BasicUserWithPermsSerializer(read_only=True, many=True)

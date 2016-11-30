from rest_framework import serializers

from sigma_core.models.user import User
from sigma_core.models.cluster import Cluster

class UserSerializerMeta():
    model = User
    exclude = ('is_staff', 'is_superuser', 'invited_to_groups', 'clusters', 'groups', )
    read_only_fields = ('last_login', 'is_active', 'photo', )
    extra_kwargs = {'password': {'write_only': True, 'required': False}}


class MinimalUserSerializer(serializers.ModelSerializer):
    """
    Serialize an User with minimal data.
    """
    class Meta:
        model = User
        fields = ('id', 'lastname', 'firstname', 'is_active', 'clusters_ids', )
        read_only_fields = ('is_active', )

    clusters_ids = serializers.PrimaryKeyRelatedField(queryset=Cluster.objects.all(), many=True, source='clusters')


class UserSerializer(serializers.ModelSerializer):
    """
    Serialize an User with related keys.
    """
    class Meta(UserSerializerMeta):
        pass

    clusters_ids = serializers.PrimaryKeyRelatedField(queryset=Cluster.objects.all(), many=True, source='clusters')

    def create(self, validated_data):
        from sigma_core.models.group_member import GroupMember
        from sigma_core.models.cluster import Cluster

        request = self.context['request']
        input_clusters_ids = request.data.get('clusters_ids', [])
        if request.user.is_sigma_admin():
            valid_clusters_ids = Cluster.objects.filter(pk__in=input_clusters_ids).values_list('id', flat=True)
        else:
            valid_clusters_ids = GroupMember.objects.filter(user=request.user, group__in=input_clusters_ids, perm_rank__gte=Cluster.ADMINISTRATOR_RANK).values_list('group', flat=True)

        if set(input_clusters_ids) != set(valid_clusters_ids):
            raise serializers.ValidationError("Cluster list: incorrect values")
        return super().create(validated_data)


class MyUserSerializer(UserSerializer):
    """
    Serialize current User with related keys.
    """
    class Meta(UserSerializerMeta):
        pass

    invited_to_groups_ids = serializers.PrimaryKeyRelatedField(read_only=True, many=True, source='invited_to_groups')

from rest_framework import serializers
from dry_rest_permissions.generics import DRYPermissionsField

from sigma_core.models.user import User
from sigma_core.models.cluster import Cluster
from sigma_files.models import Image
from sigma_files.serializers import ImageSerializer


class UserSerializerMeta():
    model = User
    exclude = ('is_staff', 'is_superuser', 'invited_to_groups', 'clusters', 'groups', )
    read_only_fields = ('last_login', 'is_active', 'photo', )
    extra_kwargs = {'password': {'write_only': True, 'required': False}}


class UserSerializer(serializers.ModelSerializer):
    """
    Serialize an User with related keys.
    """
    class Meta(UserSerializerMeta):
        pass

    photo = ImageSerializer(read_only=True)
    clusters_ids = serializers.PrimaryKeyRelatedField(queryset=Cluster.objects.all(), many=True, source='clusters')

    def create(self, fields):
        from sigma_core.models.group_member import GroupMember
        from sigma_core.models.cluster import Cluster
        try:
            request = self.context['request']
            input_clusters = request.data.get('clusters_ids')
            if request.user.is_sigma_admin():
                fields['clusters_ids'] = Cluster.objects.filter(pk__in=input_clusters).values_list('id', flat=True)
            else:
                fields['clusters_ids'] = GroupMember.objects.filter(user=request.user, group__in=input_clusters).values_list('group', flat=True)
        except ValueError:
            raise serializers.ValidationError("Cluster list: bad format")
        if input_clusters != list(fields['clusters_ids']):
            raise serializers.ValidationError("Cluster list: incorrect values")
        return super().create(fields)


class UserWithPermsSerializer(UserSerializer):
    """
    Serialize an User with related keys and add current user's permissions on the serialized User.
    """
    class Meta(UserSerializerMeta):
        pass

    permissions = DRYPermissionsField(read_only=True)


class MyUserWithPermsSerializer(UserWithPermsSerializer):
    """
    Serialize current User (with permissions).
    """
    class Meta(UserSerializerMeta):
        pass

    invited_to_groups_ids = serializers.PrimaryKeyRelatedField(read_only=True, many=True, source='invited_to_groups')

from rest_framework import serializers
from dry_rest_permissions.generics import DRYPermissionsField

from sigma_core.models.user import User
from sigma_core.serializers.group_member import GroupMemberSerializer_Group
#from sigma_core.serializers.cluster import BasicClusterSerializer
from sigma_files.models import Image
from sigma_files.serializers import ImageSerializer


class BasicUserSerializerMeta():
    model = User
    exclude = ('is_staff', 'is_superuser', 'invited_to_groups', )
    read_only_fields = ('last_login', 'is_active', 'photo', 'clusters', ) # TODO: serialize invited_to_groups correctly
    extra_kwargs = {'password': {'write_only': True, 'required': False}}


class BasicUserSerializer(serializers.ModelSerializer):
    """
    Serialize an User without relations.
    """
    class Meta(BasicUserSerializerMeta):
        pass

    photo = ImageSerializer(read_only=True)


class BasicUserWithPermsSerializer(BasicUserSerializer):
    """
    Serialize an User without relations and add current user's permissions on the serialized User.
    """
    class Meta(BasicUserSerializerMeta):
        pass

    permissions = DRYPermissionsField(read_only=True)

    def create(self, fields):
        request = self.context['request']
        clusters = request.data.get('clusters')
        # TODO: Check that the user cluster is allowed ?
        # TODO: Create related GroupMember ?
        return super().create(fields)


class DetailedUserSerializer(BasicUserSerializer):
    """
    Serialize full data about an User.
    """
    class Meta(BasicUserSerializerMeta):
        pass

    memberships = GroupMemberSerializer_Group(read_only=True, many=True)


class DetailedUserWithPermsSerializer(DetailedUserSerializer):
    """
    Serialize full data about an User and add current user's permissions on the serialized User.
    """
    class Meta(BasicUserSerializerMeta):
        pass

    permissions = DRYPermissionsField(read_only=True)


class MyUserDetailsWithPermsSerializer(DetailedUserWithPermsSerializer):
    """
    Serialize full data about current User (with permissions).
    """
    class Meta(BasicUserSerializerMeta):
        exclude = ('is_staff', 'is_superuser', )
        read_only_fields = BasicUserSerializerMeta.read_only_fields + ('invited_to_groups', )

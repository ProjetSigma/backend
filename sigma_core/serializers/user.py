from rest_framework import serializers
from dry_rest_permissions.generics import DRYPermissionsField

from sigma_core.models.user import User

class BasicUserSerializerMeta(object):
    model = User
    exclude = ('is_staff', 'is_superuser', 'invited_to_groups', )
    read_only_fields = ('last_login', 'is_active', ) # TODO: serialize invited_to_groups correctly
    extra_kwargs = {'password': {'write_only': True, 'required': False}}

class BasicUserSerializer(serializers.ModelSerializer):
    """
    Serialize an User without relations.
    """
    class Meta(BasicUserSerializerMeta):
        pass


from sigma_core.serializers.group_member import GroupMemberSerializer_WithGroup

class BasicUserWithPermsSerializer(BasicUserSerializer):
    """
    Serialize an User without relations and add current user's permissions on the serialized User.
    """
    class Meta(BasicUserSerializerMeta):
        pass

    permissions = DRYPermissionsField(read_only=True)


class DetailedUserSerializer(BasicUserSerializer):
    """
    Serialize full data about an User.
    """
    class Meta(BasicUserSerializerMeta):
        exclude = ('is_staff', 'is_superuser', )
        read_only_fields = BasicUserSerializerMeta.read_only_fields + ('invited_to_groups', )

    memberships = GroupMemberSerializer_WithGroup(read_only=True, many=True)


class DetailedUserWithPermsSerializer(DetailedUserSerializer):
    """
    Serialize full data about an User and add current user's permissions on the serialized User.
    """
    class Meta(BasicUserSerializerMeta):
        exclude = ('is_staff', 'is_superuser', )
        read_only_fields = BasicUserSerializerMeta.read_only_fields + ('invited_to_groups', )

    permissions = DRYPermissionsField(read_only=True)

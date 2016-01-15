from django.http import Http404

from rest_framework import viewsets, decorators, status, mixins
from rest_framework.response import Response
from rest_framework_extensions.mixins import DetailSerializerMixin
from dry_rest_permissions.generics import DRYPermissions

from sigma_core.models.user import User
from sigma_core.models.group_member import GroupMember
from sigma_core.serializers.user import BasicUserWithPermsSerializer, DetailedUserWithPermsSerializer, DetailedUserSerializer
from sigma_core.serializers.group_member import GroupMemberSerializer, GroupMemberSerializer_WithUserAndGroup

class GroupMemberViewSet(DetailSerializerMixin, viewsets.ModelViewSet):
    queryset = GroupMember.objects.select_related('group', 'user')
    serializer_class = GroupMemberSerializer
    queryset_detail = queryset
    serializer_detail_class = GroupMemberSerializer_WithUserAndGroup
    filter_fields = ('user', 'group', )

    # def create(self, request):
    #     pass

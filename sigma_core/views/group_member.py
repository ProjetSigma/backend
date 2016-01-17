from django.http import Http404

from rest_framework import viewsets, decorators, status, mixins
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
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
    permission_classes = [IsAuthenticated, DRYPermissions, ]
    filter_fields = ('user', 'group', )

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PUT']:
            return GroupMemberSerializer
        return super(GroupMemberViewSet, self).get_serializer_class()

    def create(self, request):
        serializer = GroupMemberSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        mem = serializer.save()
        s = GroupMemberSerializer_WithUserAndGroup(mem)
        return Response(s.data, status=status.HTTP_201_CREATED)

    # def update(self, request, pk=None):
    #     pass
    #
    # @decorators.detail_route(methods=['put'])
    # def accept(self, request, pk=None):
    #     pass
    #
    # @decorators.detail_route(methods=['put'])
    # def decline(self, request, pk=None):
    #     pass

from django.http import Http404

from rest_framework import viewsets, decorators, status, mixins
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from dry_rest_permissions.generics import DRYPermissions

from sigma_core.models.user import User
from sigma_core.models.group_member import GroupMember
from sigma_core.serializers.user import BasicUserWithPermsSerializer, DetailedUserWithPermsSerializer, DetailedUserSerializer
from sigma_core.serializers.group_member import GroupMemberSerializer

class GroupMemberViewSet(viewsets.ModelViewSet):
    queryset = GroupMember.objects.select_related('group', 'user')
    serializer_class = GroupMemberSerializer
    permission_classes = [IsAuthenticated, DRYPermissions, ]
    filter_fields = ('user', 'group', )

    def create(self, request):
        serializer = GroupMemberSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        mem = serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # def update(self, request, pk=None):
    #     pass
    #
    # @decorators.detail_route(methods=['put'])
    # def promote(self, request, pk=None):
    #     pass
    #
    # @decorators.detail_route(methods=['put'])
    # def demote(self, request, pk=None):
    #     pass

    @decorators.detail_route(methods=['put'])
    def accept_join_request(self, request, pk=None):
        try:
            gm = GroupMember.objects.select_related('group').get(pk=pk)
        except GroupMember.DoesNotExist:
            raise Http404()

        gm.perm_rank = 1 # default_perm_rank should be 0, so validation is to set perm_rank to 1
        gm.save()

        # TODO: notify user of that change

        s = GroupMemberSerializer(gm)
        return Response(s.data, status=status.HTTP_200_OK)

    # @decorators.detail_route(methods=['put'])
    # def kick(self, request, pk=None):
    #     pass
    #

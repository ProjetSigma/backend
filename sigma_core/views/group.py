from django.http import Http404
from django.db.models import Q

from rest_framework import viewsets, decorators, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import detail_route, list_route
from dry_rest_permissions.generics import DRYPermissionFiltersBase


from sigma_core.models.group import Group
from sigma_core.serializers.group import GroupSerializer

from sigma_core.models.group_field import GroupField
from sigma_core.serializers.group_field import GroupFieldSerializer

from sigma_core.models.user import User
from sigma_core.models.group_member import GroupMember


class GroupFilterBackend(DRYPermissionFiltersBase):
    def filter_queryset(self, request, queryset, view):
        """
        Limits all list requests w.r.t the Normal Rules of Visibility.
        """
        if request.user.is_sigma_admin():
            return queryset

        #invited_to_groups_ids = request.user.invited_to_groups.all().values_list('id', flat=True)
        user_groups_ids = request.user.memberships.values_list('group_id', flat=True)
        return queryset.prefetch_related('memberships', 'group_parents') \
            .filter(Q(is_private=False) | Q(memberships__user=request.user) | Q(group_parents__id__in=user_groups_ids)) \
            .distinct()


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated, ]
    filter_backends = (GroupFilterBackend, )

    @staticmethod
    def getGroup(pk):
        try:
            group = Group.objects.get(pk=pk)
        except Group.DoesNotExist:
            raise Http404("Group %d not found" % pk)
        return group

    def update(self, request, pk=None):
        group = getGroup(pk)
        if not request.user.can_modify_group_infos(group):
            return Response(status=status.HTTP_403_FORBIDDEN)
        return super(GroupViewSet, self).update(request, pk)


    @detail_route(methods=['get'])
    def members(self, request, pk=None):
        group = getGroup(pk)



    

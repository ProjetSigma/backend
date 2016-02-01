from django.http import Http404
from django.db.models import Q

from rest_framework import viewsets, decorators, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from dry_rest_permissions.generics import DRYPermissions, DRYPermissionFiltersBase

from sigma_core.models.user import User
from sigma_core.models.group import Group
from sigma_core.serializers.group import GroupSerializer


class GroupFilterBackend(DRYPermissionFiltersBase):
    def filter_list_queryset(self, request, queryset, view):
        """
        Limits all list requests to only be seen by the members or public groups.
        """
        return queryset.prefetch_related('memberships__user').filter(Q(visibility=Group.VIS_PUBLIC) | Q(memberships__user=request.user)).distinct()


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated, DRYPermissions, ]
    filter_backends = (GroupFilterBackend, )

    @decorators.detail_route(methods=['put'])
    def invite(self, request, pk=None):
        try:
            group = Group.objects.get(pk=pk)
            if not request.user.can_invite(group):
                return Response(status=status.HTTP_403_FORBIDDEN)

            user = User.objects.get(pk=request.data.get('user', None))
            group.invited_users.add(user)
            # user.notify() # TODO: Notification

            s = GroupSerializer(group)
            return Response(s.data, status=status.HTTP_200_OK)
        except Group.DoesNotExist:
            raise Http404("Group %d not found" % pk)
        except User.DoesNotExist:
            raise Http404("User %d not found" % request.data.get('user', None))

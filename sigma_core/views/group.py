from django.http import Http404
from django.db.models import Q

from rest_framework import viewsets, decorators, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from dry_rest_permissions.generics import DRYPermissions, DRYPermissionFiltersBase

from sigma_core.models.user import User
from sigma_core.models.group import Group
from sigma_core.models.group_member import GroupMember
from sigma_core.serializers.group import GroupSerializer


class GroupFilterBackend(DRYPermissionFiltersBase):
    def filter_queryset(self, request, queryset, view):
        """
        Limits all list requests w.r.t the Normal Rules of Visibility.
        """
        if request.user.is_sigma_admin():
            return queryset
        invited_to_groups_ids = request.user.invited_to_groups.all().values_list('id', flat=True)
        return queryset.prefetch_related('memberships') \
            .filter(Q(is_private=False) | Q(memberships__user=request.user) | Q(id__in=invited_to_groups_ids)) \
            .distinct()  # add: Q(parents__in=request.user.memberships__group) when GroupAcknowledgment is set up


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated, DRYPermissions, ]
    filter_backends = (GroupFilterBackend, )

    @decorators.detail_route(methods=['put'])
    def invite(self, request, pk=None):
        """
        Invite an user in group pk.
        ---
        omit_serializer: true
        parameters_strategy:
            form: replace
        parameters:
            - name: user
              type: integer
              required: true
        """
        try:
            group = Group.objects.get(pk=pk)
            user = User.objects.get(pk=request.data.get('user', None))
            if not request.user.can_invite(group):
                return Response(status=status.HTTP_403_FORBIDDEN)

            # Already group member ?
            try:
                GroupMember.objects.get(user=user.id, group=group.id)
                return Response("Already Group member", status=status.HTTP_400_BAD_REQUEST)
            except GroupMember.DoesNotExist:
                pass

            group.invited_users.add(user)
            # user.notify() # TODO: Notification
            s = GroupSerializer(group)
            return Response(s.data, status=status.HTTP_200_OK)

        except Group.DoesNotExist:
            raise Http404("Group %d not found" % pk)
        except User.DoesNotExist:
            raise Http404("User %d not found" % request.data.get('user', None))

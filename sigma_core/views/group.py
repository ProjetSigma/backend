from django.http import Http404
from django.db.models import Q

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import detail_route, list_route
from dry_rest_permissions.generics import DRYPermissions

from sigma_core.models.group import Group
from sigma_core.serializers.group import GroupSerializer

from sigma_core.models.user import User
from sigma_core.models.group_member import GroupMember

#TO DO : REPLACE IT LATER ONCE ADEQUATE FUNCTIONS ARE CREATED
# class GroupFilterBackend(DRYPermissionFiltersBase):
#     def filter_queryset(self, request, queryset, view):
#         """
#         Limits all list requests w.r.t the Normal Rules of Visibility.
#         """
#         if request.user.is_sigma_admin():
#             return queryset
#
#         #invited_to_groups_ids = request.user.invited_to_groups.all().values_list('id', flat=True)
#         user_groups_ids = request.user.memberships.values_list('group_id', flat=True)
#         return queryset.prefetch_related('memberships', 'group_parents') \
#             .filter(Q(is_private=False) | Q(memberships__user=request.user) | Q(group_parents__id__in=user_groups_ids)) \
#             .distinct()
#

class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated, DRYPermissions]
    # filter_backends = (GroupFilterBackend, )


    def perform_create(self, serializer):
        gr=serializer.save()
        GroupMember.objects.create(user=request.user, group=gr, is_administrator=True)

#TO DO : filter the list
#    def list(self, request):


    def quit(self, request, pk):
        try:
            m_ship=GroupMember.objects.get(user=request.user,group=Group.objects.get(pk=pk))
            if not m_ship.is_super_administrator:
                m_ship.destroy()
            else:
                return Response(status=status.HTTP_403_FORBIDDEN)
        except GroupMember.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except Group.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    #In the destroy function, with the ON DELETE CASCADE function of Django
    #So no need to delete memberships and invitations

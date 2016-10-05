from django.http import Http404
from django.db.models import Prefetch, Q

from rest_framework import viewsets, decorators, status, mixins
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import BaseFilterBackend

from sigma_core.models.user import User
from sigma_core.models.group import Group, GroupAcknowledgment
from sigma_core.models.group_member import GroupMember
from sigma_core.serializers.group_member import GroupMemberSerializer

from dry_rest_permissions.generics import DRYPermissions

class GroupMemberFilterBackend(BaseFilterBackend):
    filter_q = {
        'user': lambda u: Q(user=u),
        'group': lambda g: Q(group=g)
    }

    def filter_queryset(self, request, queryset, view):
        """
        Limits all list requests w.r.t the Normal Rules of Visibility.
        """
        #Will be changed later
        # I can see a GroupMember if one of the following conditions is met:
        #  - I am member of the group
        #  - I am invited to the group
        #  - (the group is public OR acknowledged by one of my groups) AND I can see the user w.r.t. NRVU

        return queryset


class GroupMemberViewSet(viewsets.ModelViewSet):
    queryset = GroupMember.objects.select_related('group', 'user')
    serializer_class = GroupMemberSerializer
    permission_classes = [IsAuthenticated, DRYPermissions]
    filter_backends = (GroupMemberFilterBackend, )


    def list(self, request):
        """
        ---
        parameters_strategy:
            query: replace
        parameters:
            - name: user
              type: integer
              paramType: query
            - name: group
              type: integer
              paramType: query
        """
        return super().list(request)



    def can_modify_basic_rights(self, request, modified_mship, my_mship):
        #trights to become superadmin or admin are not concerned
        if my_mship.is_super_administrator:
            return True

        if my_mship.is_administrator and not modified_mship.is_administrator:
            return True

        return False

    def can_promote_admin_or_superadmin(self,request,modified_mship,my_mship):
        #only a super_administrator can do that
        return my_mship.is_super_administrator

    # def can_be_contacted(self,request,modified_mship,my_mship):
    #
    #     if my_mship.id == modified_mship.id:
    #         return True
    #
    #     if my_mship.is_administrator:
    #         return True



    def update(self, request, pk=None):
        """
        Change the rights of a member of the group pk.
        ---
        """
        #override to change the status of super_administrator if he wants to appoint someone else
        from sigma_core.models.group import Group
        try:
            my_mship = GroupMember.objects.all().get(group=group, user=request.user)
            right_to_change = request.data.get('right_to_change', None)

            if right_to_change=="is_super_administrator":
                my_mship.is_super_administrator=False
                my_mship.save()
        except GroupMember.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        except request.data.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)


        return super(viewsets.ModelViewSet, self).update(self,request,pk)

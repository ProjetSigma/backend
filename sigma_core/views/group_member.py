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


class GroupMemberFilterBackend(BaseFilterBackend):
    filter_q = {
        'user': lambda u: Q(user=u),
        'group': lambda g: Q(group=g)
    }

    def filter_queryset(self, request, queryset, view):
        """
        Limits all list requests w.r.t the Normal Rules of Visibility.
        """
        if not request.user.is_sigma_admin():
            invited_to_groups_ids = request.user.invited_to_groups.all().values_list('id', flat=True)
            user_groups_ids = request.user.memberships.filter(is_accepted=True).values_list('group_id', flat=True)
            # I can see a GroupMember if one of the following conditions is met:
            #  - I am member of the group
            #  - I am invited to the group
            #  - (the group is public OR acknowledged by one of my groups) AND I can see the user w.r.t. NRVU
            queryset = queryset.prefetch_related(
                Prefetch('user__memberships', queryset=GroupMember.objects.filter(is_accepted=True)),
                Prefetch('group__group_parents', queryset=GroupAcknowledgment.objects.filter(validated=True))
            ).filter(Q(user_id=request.user.id) | Q(group_id__in=user_groups_ids) | Q(group_id__in=invited_to_groups_ids) | (
                (Q(group__is_private=False) | Q(group__group_parents__id__in=user_groups_ids)) &
                    Q(user__memberships__group_id__in=user_groups_ids)
            ))

        for (param, q) in self.filter_q.items():
            x = request.query_params.get(param, None)
            if x is not None:
                queryset = queryset.filter(q(x))

        return queryset.distinct()


class GroupMemberViewSet(viewsets.ModelViewSet):
    queryset = GroupMember.objects.select_related('group', 'user')
    serializer_class = GroupMemberSerializer
    permission_classes = [IsAuthenticated, ]
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

    def create(self, request):
        serializer = GroupMemberSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        if request.data.get('user_id', None) != request.user.id and not request.user.is_sigma_admin():
            return Response('You cannot add someone else to a group', status=status.HTTP_403_FORBIDDEN)

        try:
            group = Group.objects.get(pk=request.data.get('group_id', None))
        except Group.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if not group.can_anyone_join:
            return Response('You cannot join this group without an invitation', status=status.HTTP_403_FORBIDDEN)

        mem = serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, pk=None):
        from sigma_core.models.group import Group
        try:
            modified_mship = GroupMember.objects.all().select_related('group').get(pk=pk)
            group = modified_mship.group
            my_mship = GroupMember.objects.all().get(group=group, user=request.user)
        except GroupMember.DoesNotExist:
            raise Http404()

        # You can always quit the Group (ie destroy YOUR membership)
        if my_mship.id != modified_mship.id:
            # Can't modify a admin if you're not superadmin
            if not my_mship.is_super_administrator and modified_mship.is_administrator:
                return Response(status=status.HTTP_403_FORBIDDEN)

            # Check permission
            if not my_mship.can_kick:
                return Response(status=status.HTTP_403_FORBIDDEN)

        modified_mship.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def can_modify_basic_rights(self, request, modified_mship, my_mship):
        #rights to become superadmin or admin are not concerned
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


    @decorators.detail_route(methods=['put'])
    def give_rights(self, request, pk=None):
        """
        Change the rights of a member of the group pk.
        ---
        request_serializer: null
        response_serializer: GroupMemberSerializer
        parameters_strategy:
            form: replace
        parameters:
            - name: right_to_change
              type: string
              possible values : is_administrator, is_super_administrator,
              can_invite, can_be_contacted, can_kick, can_modify_group_infos,
              can_publish
              required: true
        """
        from sigma_core.models.group import Group
        try:
            modified_mship = GroupMember.objects.all().select_related('group').get(pk=pk)
            my_mship = GroupMember.objects.all().get(group=modified_mship.group, user=request.user)
        except GroupMember.DoesNotExist:
            raise Http404()

        right_to_change = request.data.get('right_to_change', None)

        if my_mship.can_modify_basic_rights and right_to_change in basic_rights_string:
            if right_to_change=="can_invite":
                modified_mship.can_invite= not modified_mship.can_invite
            elif right_to_change=="can_kick":
                modified_mship.can_kick= not modified_mship.can_kick
            elif right_to_change=="can_publish":
                modified_mship.can_publish= not modified_mship.can_publish
            elif right_to_change=="can_modify_group_infos":
                modified_mship.can_modify_group_infos= not modified_mship.can_modify_group_infos
            elif right_to_change=="can_be_contacted":
                modified_mship.can_be_contacted= not modified_mship.can_be_contacted

        elif my_mship.can_promote_admin_or_superadmin:
            if right_to_change=="is_administrator":
                modified_mship.is_administrator= not modified_mship.is_administrator
            else:
                #there can only be one super admin
                modified_mship.is_super_administrator=True
                my_mship.is_super_administrator=False

            if modified_mship.is_administrator:
                #we give him all the rights (except can_be_contacted, he gets to choose)
                modified_mship.can_invite=True
                modified_mship.can_kick=True
                modified_mship.can_publish=True

        else:
            return Response(status=status.HTTP_403_FORBIDDEN)

        my_mship.save()
        modified_mship.save()

        return Response(GroupMemberSerializer(modified_mship).data, status=status.HTTP_200_OK)

    @decorators.detail_route(methods=['put'])
    def accept_join_request(self, request, pk=None):
        """
        Validate a pending membership request.
        ---
        request_serializer: null
        response_serializer: GroupMemberSerializer
        """
        try:
            gm = GroupMember.objects.select_related('group').get(pk=pk)
        except GroupMember.DoesNotExist:
            raise Http404()

        if not request.user.can_accept_join_requests(gm.group):
            return Response(status=status.HTTP_403_FORBIDDEN)

        gm.is_accepted = True
        gm.save()

        # TODO: notify user of that change

        s = GroupMemberSerializer(gm)
        return Response(s.data, status=status.HTTP_200_OK)

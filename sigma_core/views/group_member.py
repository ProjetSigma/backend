from django.http import Http404
from django.db.models import Prefetch, Q

from rest_framework import viewsets, decorators, status, mixins
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import BaseFilterBackend

from sigma_core.models.user import User
from sigma_core.models.group import GroupAcknowledgment
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
            user_groups_ids = request.user.memberships.filter(perm_rank__gte=1).values_list('group_id', flat=True)
            # I can see a GroupMember if one of the following conditions is met:
            #  - I am member of the group
            #  - I am invited to the group
            #  - (the group is public OR acknowledged by one of my groups) AND I can see the user w.r.t. NRVU
            queryset = queryset.prefetch_related(
                Prefetch('user__memberships', queryset=GroupMember.objects.filter(perm_rank__gte=1)),
                Prefetch('group__group_parents', queryset=GroupAcknowledgment.objects.filter(validated=True))
            ).filter(Q(group_id__in=user_groups_ids) | Q(group_id__in=invited_to_groups_ids) | (
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

    def list(self, request): # TODO: filter on groups request.user belongs to
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
            # Can't modify someone higher than you
            if my_mship.perm_rank <= modified_mship.perm_rank:
                return Response(status=status.HTTP_403_FORBIDDEN)

            # Check permission
            if group.req_rank_kick > my_mship.perm_rank:
                return Response(status=status.HTTP_403_FORBIDDEN)

        modified_mship.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def can_rank(self, request, modified_mship, my_mship, perm_rank_new):
        # You can demote yourself:
        demote_self = modified_mship.id == my_mship.id and perm_rank_new < my_mship.perm_rank
        group = modified_mship.group

        # Can't modify someone higher than you, or set rank to higher than you
        if (my_mship.perm_rank <= modified_mship.perm_rank or my_mship.perm_rank <= perm_rank_new) and not demote_self:
            return False

        # promote
        if perm_rank_new > modified_mship.perm_rank:
            if group.req_rank_promote > my_mship.perm_rank:
                return False
        # demote
        else:
            if group.req_rank_demote > my_mship.perm_rank and not demote_self:
                return False
        return True

    @decorators.detail_route(methods=['put'])
    def rank(self, request, pk=None):
        """
        Change the perm_rank of a member of the group pk.
        ---
        request_serializer: null
        response_serializer: GroupMemberSerializer
        parameters_strategy:
            form: replace
        parameters:
            - name: perm_rank
              type: integer
              required: true
        """
        from sigma_core.models.group import Group
        try:
            modified_mship = GroupMember.objects.all().select_related('group').get(pk=pk)
            my_mship = GroupMember.objects.all().get(group=modified_mship.group, user=request.user)
        except GroupMember.DoesNotExist:
            raise Http404()

        perm_rank_new = request.data.get('perm_rank', None)

        try:
            if perm_rank_new > Group.ADMINISTRATOR_RANK or perm_rank_new < 1 or perm_rank_new == modified_mship.perm_rank:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        except TypeError:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if not self.can_rank(request, modified_mship, my_mship, perm_rank_new):
            return Response(status=status.HTTP_403_FORBIDDEN)

        modified_mship.perm_rank = perm_rank_new
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

        gm.perm_rank = 1 # default_perm_rank should be 0, so validation is to set perm_rank to 1
        gm.save()

        # TODO: notify user of that change

        s = GroupMemberSerializer(gm)
        return Response(s.data, status=status.HTTP_200_OK)

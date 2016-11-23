from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated

from dry_rest_permissions.generics import DRYPermissions

from sigma_core.models.group_invitation import GroupInvitation
from sigma_core.serializers.group_invitation import GroupInvitationSerializer
from rest_framework.decorators import detail_route


class GroupInvitationViewSet(viewsets.ModelViewSet):
    queryset = GroupInvitation.objects.all()
    serializer_class = GroupInvitationSerializer
    permission_classes = [IsAuthenticated, DRYPermissions]

    @detail_route(methods=['post'])
    def confirm(self, request, pk):

        from sigma_core.models.group_member import GroupMember
        try:
            invit = GroupInvitation.objects.get(pk=pk)
            new_member = invit.invitee
            group = invit.group

            GroupMember.objets.create(user=new_member,group=group)
            invit.destroy()
        except GroupInvitation.DoesNotExist:
            raise Http404("Invitation not found")

    #destroy method created on its own ?

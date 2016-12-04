from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated

from dry_rest_permissions.generics import DRYPermissions

from sigma_core.models.group_invitation import GroupInvitation
from sigma_core.serializers.group_invitation import GroupInvitationSerializer
from rest_framework.decorators import detail_route
from sigma_core.models.group_member import GroupMember

class GroupInvitationViewSet(viewsets.ModelViewSet):
    queryset = GroupInvitation.objects.all()
    serializer_class = GroupInvitationSerializer
    permission_classes = [IsAuthenticated, DRYPermissions]


    @detail_route(methods=['post'])
    def confirm(self, request, pk):
        try:
            invit = GroupInvitation.objects.get(pk=pk)
            new_member = invit.invitee
            group = invit.group

            GroupMember.objets.create(user=new_member,group=group)
            invit.destroy()
        except GroupInvitation.DoesNotExist:
            raise Http404("Invitation not found")
        return Response(request.data,status=status.HTTP_200_OK)


    def create(self, request):
        invit_serializer=GroupInvitationSerializer(data=request.data)
        if invit_serializer.is_valid():
            try: #if the invitation already exists or the invitee is already a member
                GroupInvitation.objects.get(user=invit_serializer.invitee,group=invit_serializer.group)
                GroupMember.objects.get(user=invit_serializer.invitee,group=invit_serializer.group)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            except:
                pass
            if not invit_serializer.group.need_validation_to_join:
                GroupMember.objets.create(user=invit_serializer.invitee,group=invit_serializer.group)
            else:
                invit_serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

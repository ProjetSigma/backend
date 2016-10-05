from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from dry_rest_permissions.generics import DRYPermissions

from sigma_core.models.group_invitation import GroupInvitation
from sigma_core.serializers.group_invitation import GroupInvitationSerializer

class GroupInvitationViewSet(viewsets.ModelViewSet):
    queryset = GroupInvitation.objects.all()
    serializer_class = GroupInvitationSerializer
    permission_classes = [IsAuthenticated, DRYPermissions]
    
    # @detail_route(method=['post'])
    # def confirm(self, request, pk):
        # pass
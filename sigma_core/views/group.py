from django.http import Http404

from rest_framework import viewsets, decorators, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from dry_rest_permissions.generics import DRYPermissions

from sigma_core.models.user import User
from sigma_core.models.group import Group
from sigma_core.serializers.group import GroupSerializer


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated, DRYPermissions, ]

    @decorators.detail_route(methods=['put'])
    def invite(self, request, pk=None):
        try:
            group = Group.objects.get(pk=pk)
            user = User.objects.get(pk=request.data.get('user', None))
        except Group.DoesNotExist:
            raise Http404("Group %d not found" % pk)
        except User.DoesNotExist:
            raise Http404("User %d not found" % request.data.get('user', None))

        group.invited_users.add(user)
        # TODO: notify user of this invitation

        s = GroupSerializer(group)
        return Response(s.data, status=status.HTTP_200_OK)

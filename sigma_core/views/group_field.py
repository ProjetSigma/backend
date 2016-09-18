from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from dry_rest_permissions.generics import DRYPermissions

from sigma_core.models.group_field import GroupField
from sigma_core.serializers.group_field import GroupFieldSerializer

class GroupFieldViewSet(viewsets.ModelViewSet):
    queryset = GroupField.objects.all()
    serializer_class = GroupFieldSerializer
    permission_classes = [IsAuthenticated, DRYPermissions]

    # You will never see fields for groups you are not a member of
    # def get_queryset(self):
        # from sigma_core.models.group_member import GroupMember
        # if not self.request.user.is_authenticated():
            # return self.queryset.none()
        # if self.request.user.is_sigma_admin():
            # return self.queryset
        # # @sqlperf: Find which one is the most efficient
        # my_groups = GroupMember.objects.filter(user=self.request.user.id).values_list('group', flat=True)
        # my_groups = Group.objects.filter(memberships__user=self.request.user.id)
        # return self.queryset.filter(group__in=my_groups)

        
        
    # def create(self, request):
        # serializer = GroupFieldSerializer(data=request.data)
        # if not serializer.is_valid():
            # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        # if not request.user.has_group_admin_perm(serializer.validated_data.get('group')):
            # return Response('Not group administrator', status=status.HTTP_403_FORBIDDEN)

        # serializer.save()
        # return Response(serializer.data, status=status.HTTP_201_CREATED)

    # @decorators.detail_route(methods=['post'])
    # def validate(self, request, pk):
        # """
        # For given custom field $pk, we check if the client input passes the Validation
        # """
        # from sigma_core.models.group_field import GroupField
        # if not request.user.is_authenticated():
            # return Response(status=status.HTTP_401_UNAUTHORIZED)
        # client_input = request.data.get('value')
        # if client_input is None:
            # return Response("No value given", status=status.HTTP_400_BAD_REQUEST)

        # try:
            # gf = self.get_queryset().get(id=pk)
            # try:
                # gf.validator.validate_input(gf.validator_values, client_input)
                # return Response({"status": "ok"}, status=status.HTTP_200_OK)
            # except ValidationError as err:
                # return Response({"status": "ko", "message": err.messages}, status=status.HTTP_200_OK)
            # except:
                # return Response({"status": "ko", "message": "Invalid input"}, status=status.HTTP_200_OK)
        # except:
            # return Response(status=status.HTTP_404_NOT_FOUND)

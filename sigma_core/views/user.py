from rest_framework import viewsets, decorators, status
from rest_framework.response import Response
from dry_rest_permissions.generics import DRYPermissions

from sigma_core.models.user import User
from sigma_core.serializers.user import UserSerializer, UserWithoutNamesSerializer


class UserViewSet(viewsets.ModelViewSet):
    permission_classes = (DRYPermissions, )
    queryset = User.objects.all()

    def get_serializer_class(self):
        """
        Users cannot change their lastname and firstname, but admins can.
        """
        if self.request.method == 'PUT' and not (self.request.user.is_staff or self.request.user.is_superuser):
            return UserWithoutNamesSerializer
        else:
            return UserSerializer

    @decorators.list_route(methods=['get'])
    def me(self, request):
        """
        Gives the data of the current user
        """
        if request.user.__class__.__name__ == 'AnonymousUser':
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        else:
            serializer = self.get_serializer_class()(request.user, context={'request': request})
            return Response(serializer.data)

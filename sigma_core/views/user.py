from django.http import Http404

from rest_framework import viewsets, decorators, status
from rest_framework.response import Response
from dry_rest_permissions.generics import DRYPermissions

from sigma_core.models.user import User
from sigma_core.serializers.user import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    permission_classes = (DRYPermissions, )
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def update(self, request, pk=None):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Http404()

        if (request.data['lastname'] != user.lastname or request.data['firstname'] != user.firstname):
            if not (request.user.is_staff or request.user.is_superuser):
                return Response('You cannot change your lastname or firstname', status=status.HTTP_400_BAD_REQUEST)

        return super(UserViewSet, self).update(request, pk)

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

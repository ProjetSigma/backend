from rest_framework import viewsets, decorators, status
from rest_framework.response import Response

from sigma_core.models.user import User
from sigma_core.serializers.user import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @decorators.list_route(methods=['get'])
    def me(self, request):
        """
        Gives the data of the current user
        """
        if request.user.__class__.__name__ == 'AnonymousUser':
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        else:
            serializer = self.serializer_class(request.user)
            return Response(serializer.data)

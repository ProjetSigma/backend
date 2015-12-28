import random
import string

from django.core.mail import send_mail
from django.http import Http404

from rest_framework import viewsets, decorators, status
from rest_framework.response import Response
from dry_rest_permissions.generics import DRYPermissions

from sigma_core.models.user import User
from sigma_core.serializers.user import UserSerializer


reset_mail = {
    'from_email': 'support@sigma.fr',
    'subject': 'Mot de passe Sigma',
    'message': u"""
Bonjour,
Ton mot de passe Sigma a été réinitialisé.
C'est maintenant "{password}".
Cordialement,
L'équipe Sigma.
"""
}


class UserViewSet(viewsets.ModelViewSet):
    permission_classes = (DRYPermissions, )
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def update(self, request, pk=None):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Http404()

        if ((request.data['lastname'] != user.lastname or request.data['firstname'] != user.firstname)) and not (request.user.is_staff or request.user.is_superuser):
            return Response('You cannot change your lastname or firstname', status=status.HTTP_400_BAD_REQUEST)

        return super(UserViewSet, self).update(request, pk)

    @decorators.list_route(methods=['get'])
    def me(self, request):
        """
        Give the data of the current user.
        """
        if request.user.__class__.__name__ == 'AnonymousUser':
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        else:
            serializer = self.get_serializer_class()(request.user, context={'request': request})
            return Response(serializer.data)

    @decorators.list_route(methods=['put'])
    def change_password(self, request):
        """
        Allow current user to change his password.
        ---
        omit_serializer: true
        parameters_strategy:
            form: replace
        parameters:
            - name: old_password
              type: string
            - name: password
              type: string
        """
        if request.user.__class__.__name__ == 'AnonymousUser':
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        user = request.user
        data = request.data
        if not user.check_password(data['old_password']):
            return Response("Wrong password", status=status.HTTP_403_FORBIDDEN)
        if data['password'] == "":
            return Response("'password' field cannot be empty", status=status.HTTP_400_BAD_REQUEST)

        user.set_password(data['password'])
        user.save()
        return Response('Password successfully changed', status=status.HTTP_200_OK)

    @decorators.list_route(methods=['post'])
    def reset_password(self, request):
        """
        Reset current user's password and send him an email with the new one.
        ---
        omit_serializer: true
        parameters_strategy:
            form: replace
        parameters:
            - name: email
              type: string
        """
        email = request.data.get('email')
        if email == '':
            return Response("'email' field cannot be empty", status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response('No user found with this email', status=status.HTTP_404_NOT_FOUND)

        password = ''.join(random.choice(string.ascii_lowercase + string.ascii_uppercase + string.digits) for _ in range(10))

        mail = reset_mail.copy()
        mail['recipient_list'] = [user.email]
        mail['message'] = mail['message'].format(email=user.email, password=password, name=user.get_full_name())
        send_mail(**mail)

        user.set_password(password)
        user.save()

        return Response('Password reset', status=status.HTTP_200_OK)

# -*- coding: utf-8 -*-
import random
import string
import operator
from functools import reduce

from django.core.mail import send_mail
from django.db.models import Q, Prefetch
from django.http import Http404
from django.views.decorators.csrf import csrf_exempt

from rest_framework import mixins, viewsets, decorators, status, parsers
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from sigma_core.models.user import User
from sigma_core.models.group_member import GroupMember
from sigma_core.serializers.user import UserSerializer, MinimalUserSerializer, MyUserSerializer


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


class UserViewSet(mixins.CreateModelMixin,      # Only Cluster admins can create users
                    mixins.ListModelMixin,      # Can only see members within same cluster or group
                    mixins.RetrieveModelMixin,  # Can see anybody but with different serializations
                    mixins.UpdateModelMixin,    # Only self or cluster admin
                    mixins.DestroyModelMixin,   # Only self or Sigma admin
                    viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated, ]
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def perform_create(self, serializer):
        from sigma_core.models.cluster import Cluster
        from sigma_core.models.group import Group
        serializer.save()
        # Create related GroupMember associations
        # TODO: Looks like a hacky-way to do this.
        # But how to do it properly ?
        memberships = [GroupMember(group=Group(id=c), user=User(id=serializer.data['id']),) for c in serializer.data['clusters_ids']]
        GroupMember.objects.bulk_create(memberships)

    def list(self, request, *args, **kwargs):
        """
        Get the list of users that you are allowed to see w.r.t. the Normal Rules of Visibility.
        """
        # Sigma admins can list all the users
        if request.user.is_sigma_admin():
            return super().list(self, request, args, kwargs)

        # We get visible users ids w.r.t. the Normal Rules of Visibility, based on their belongings to common clusters/groups (let's anticipate the pagination)
        # Since clusters are groups, we only check that condition for groups
        groups_ids = request.user.memberships.values_list('group_id', flat=True)
        qs = User.objects.prefetch_related('memberships').filter(is_active=True, memberships__group__id__in=groups_ids).distinct()
        s = UserSerializer(qs, many=True, context={'request': request})
        return Response(s.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        """
        Retrieve an User according to its id (pk).
        """
        # 1. Retrieve user
        try:
            user = User.objects.all().prefetch_related('clusters').select_related('photo').get(pk=pk)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        # 2. Check permissions to choose serializer
        # Admin, oneself, common cluster or common group: can see detailed user
        if request.user.is_sigma_admin() or user.id == request.user.id or request.user.has_common_cluster(user) or request.user.has_common_group(user):
            s = UserSerializer(user, context={'request': request})
        else : # Others can only see minimal information
            s = MinimalUserSerializer(user, context={'request': request})

        return Response(s.data, status=status.HTTP_200_OK)

    def update(self, request, pk=None):
        try:
            user = User.objects.prefetch_related('clusters').get(pk=pk)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        # I can update my own profile, or another's profile if I'm a sigma/cluster admin
        if not (request.user.is_sigma_admin() or int(pk) == request.user.id or request.user.is_admin_of_one_cluster(user.clusters.all())):
            return Response(status=status.HTTP_403_FORBIDDEN)

        # Names edition is allowed to sigma/clusters admins only
        if (request.data['lastname'] != user.lastname or request.data['firstname'] != user.firstname) and not request.user.is_sigma_admin() and not request.user.is_admin_of_one_cluster(user.clusters.all()):
            return Response('You cannot change your lastname or firstname', status=status.HTTP_400_BAD_REQUEST)

        return super(UserViewSet, self).update(request, pk)

    def destroy(self, request, pk=None):
        if not request.user.is_sigma_admin() and int(pk) != request.user.id:
            return Response(status=status.HTTP_403_FORBIDDEN)
        super().destroy(request, pk)

    @decorators.list_route(methods=['get'])
    def me(self, request):
        """
        Give the data of the current user.
        ---
        response_serializer: MyUserSerializer
        """
        user = User.objects.all().select_related('photo').prefetch_related(
            Prefetch('memberships', queryset=GroupMember.objects.all().select_related('group'))
        ).get(pk=request.user.id)
        s = MyUserSerializer(user, context={'request': request})
        return Response(s.data, status=status.HTTP_200_OK)

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
        PASSWORD_MIN_LENGTH = 8

        user = request.user
        data = request.data
        if not user.check_password(data['old_password']):
            return Response("Wrong password", status=status.HTTP_403_FORBIDDEN)
        if len(data['password']) < PASSWORD_MIN_LENGTH:
            return Response("'password' must be at least %d characters long" % PASSWORD_MIN_LENGTH, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(data['password'])
        user.save()
        return Response('Password successfully changed', status=status.HTTP_200_OK)

    #Dangerous to send a password in clear...
    @decorators.list_route(methods=['post'], permission_classes=[AllowAny])
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

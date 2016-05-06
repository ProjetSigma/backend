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
from sigma_core.serializers.user import UserSerializer, MyUserWithPermsSerializer


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
                    mixins.RetrieveModelMixin,  # Idem
                    mixins.UpdateModelMixin,    # Only self
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
        memberships = []
        for cluster in serializer.data['clusters_ids']:
            memberships += [GroupMember(group=Group(id=cluster), user=User(id=serializer.data['id']), perm_rank=Cluster.DEFAULT_MEMBER_RANK)]
        GroupMember.objects.bulk_create(memberships)

    def list(self, request, *args, **kwargs):
        """
        Get the list of users that you are allowed to see.
        """
        # Sigma admins can list all the users
        if request.user.is_sigma_admin():
            return super().list(self, request, args, kwargs)

        # We get visible users ids, based on their belongings to common clusters/groups (let's anticipate the pagination)
        # Since clusters are groups, we only check that condition for groups
        groups_ids = request.user.memberships.all().values_list('group_id', flat=True)
        users_ids = User.objects.all().prefetch_related('memberships').filter(memberships__group__id__in=groups_ids).distinct().values_list('id', flat=True)

        qs = User.objects.filter(id__in=users_ids)
        s =UserSerializer(qs, many=True, context={'request': request})
        return Response(s.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        """
        Retrieve an User according to its id (pk).
        """
        # 1. Check if we are allowed to see this user
        user = User.objects.only('id').filter(pk=pk).prefetch_related('clusters').get()

        # 2. Check what we can see from this User
        qs = User.objects.all().select_related('photo').prefetch_related('clusters')
        gm = GroupMember.objects.select_related('group')
        # Admin: can see everything
        if request.user.is_sigma_admin() or user.id == request.user.id:
            user = qs.prefetch_related(
                Prefetch('memberships', queryset=gm)
            ).get(pk=pk)
        # Same cluster: can see public groups memberships
        elif request.user.has_common_cluster(user):
            user = qs.prefetch_related(
                Prefetch('memberships', queryset=gm.filter(
                    Q(group__is_private=False) | Q(group__in=request.user.get_groups_with_confirmed_membership()))
                )
            ).get(pk=pk)
        # In the general case, we only see common Group memberships
        # Also verify that we are on the same Group
        else:
            user = qs.prefetch_related(
                Prefetch('memberships', queryset=gm.filter(group__in=request.user.get_groups_with_confirmed_membership()))
            ).get(pk=pk)
            if not user.memberships.exists(): # No membership visible => User not visible
                return Response(status=status.HTTP_404_NOT_FOUND)

        s =UserSerializer(user, context={'request': request})
        return Response(s.data, status=status.HTTP_200_OK)

    def destroy(self, request, pk=None):
        if not request.user.is_sigma_admin() and int(pk) != request.user.id:
            return Response(status=status.HTTP_404_NOT_FOUND)
        super().destroy(request, pk)

    def update(self, request, pk=None):
        if not request.user.is_sigma_admin() and int(pk) != request.user.id:
            return Response(status=status.HTTP_404_NOT_FOUND)

        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise Http404()

        # Names edition is allowed to Sigma admins only
        if ((request.data['lastname'] != user.lastname or request.data['firstname'] != user.firstname)) and not request.user.is_sigma_admin():
            return Response('You cannot change your lastname or firstname', status=status.HTTP_400_BAD_REQUEST)

        return super(UserViewSet, self).update(request, pk)

    @decorators.list_route(methods=['get'])
    def me(self, request):
        """
        Give the data of the current user.
        ---
        response_serializer: MyUserWithPermsSerializer
        """
        if request.user.__class__.__name__ == 'AnonymousUser':
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        else:
            user = User.objects.all().select_related('photo').prefetch_related(
                Prefetch('memberships', queryset=GroupMember.objects.all().select_related('group'))
            ).get(pk=request.user.id)
            s = MyUserWithPermsSerializer(user, context={'request': request})
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

        if request.user.__class__.__name__ == 'AnonymousUser':
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        user = request.user
        data = request.data
        if not user.check_password(data['old_password']):
            return Response("Wrong password", status=status.HTTP_403_FORBIDDEN)
        if len(data['password']) < PASSWORD_MIN_LENGTH:
            return Response("'password' must be at least %d characters long" % PASSWORD_MIN_LENGTH, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(data['password'])
        user.save()
        return Response('Password successfully changed', status=status.HTTP_200_OK)

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

    @decorators.detail_route(methods=['post'])
    @decorators.parser_classes([parsers.MultiPartParser, ])
    def addphoto(self, request, pk=None):
        """
        Add a profile photo to user "pk".
        ---
        omit_serializer: true
        parameters_strategy:
            form: replace
        parameters:
            - name: file
              type: file
              required: true
        """
        from sigma_files.models import Image
        from sigma_files.serializers import ImageSerializer_WithoutPerms as ImageSerializer

        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise Http404()

        s = ImageSerializer(data=request.data, context={'request': request})
        s.is_valid(raise_exception=True)
        img = s.save()
        img.owner = user
        img.save()
        user.photo = img
        user.save()

        return Response(status=status.HTTP_201_CREATED)

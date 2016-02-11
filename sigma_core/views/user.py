# -*- coding: utf-8 -*-
import random
import string

from django.core.mail import send_mail
from django.db.models import Q, Prefetch
from django.http import Http404
from django.views.decorators.csrf import csrf_exempt

from rest_framework import mixins, viewsets, decorators, status, parsers
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from dry_rest_permissions.generics import DRYPermissions, DRYPermissionFiltersBase

from sigma_core.models.user import User
from sigma_core.models.group_member import GroupMember
from sigma_core.serializers.user import BasicUserWithPermsSerializer, DetailedUserWithPermsSerializer, MyUserDetailsWithPermsSerializer


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

class VisibleUsersFilterBackend(DRYPermissionFiltersBase):
    def filter_queryset(self, request, queryset, view):
        """
        Never display information for Users who have no group (/cluster) in common
        Rq: If we are in the same cluster, we have a group in common.
        """
        if request.user.is_sigma_admin():
            return queryset
        if view.action is "retrieve":
            from sigma_core.models.group_member import GroupMember
            # @sqlperf: Maybe it is more efficient with only one Query?
            view.my_groups = GroupMember.objects.filter(Q(user=request.user) & Q(perm_rank__gte=1)).values_list('group', flat=True)
            view.visible_users_ids = GroupMember.objects.filter(group__in=view.my_groups).values('user')
            return queryset.filter(Q(pk__in=view.visible_users_ids) | Q(pk=request.user.id))
        elif view.action is "update" or view.action is "destroy": # Destroy
            return queryset.filter(pk=request.user.id)
        return queryset

class UserViewSet(mixins.CreateModelMixin,      # Only Cluster admins can create users
                    mixins.ListModelMixin,      # Only sigma admins can list
                    mixins.RetrieveModelMixin,  # Can only see members within same group or cluster
                    mixins.UpdateModelMixin,    # Only self
                    mixins.DestroyModelMixin,   # ??
                    viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated, ]#DRYPermissions, ]
    queryset = User.objects.all()
    serializer_class = BasicUserWithPermsSerializer # by default, basic data and permissions
    filter_backends = (VisibleUsersFilterBackend, )

    def list(self, request, *args, **kwargs):
        # Only sigma admins can list all the users
        if request.user.is_sigma_admin():
            return super().list(self, request, args, kwargs)
        return Response(status=status.HTTP_403_FORBIDDEN)

    def retrieve(self, request, pk=None):
        """
        Retrieve an User according to its id (pk).
        ---
        response_serializer: DetailedUserWithPermsSerializer
        """
        # 1. Check if we are allowed to see this user
        user = self.get_object()

        # 2. Check what we can see from this User
        # Admin: can see everything
        if request.user.is_sigma_admin():
            user = User.objects.all().select_related('photo').prefetch_related(
                'clusters',
                Prefetch('memberships', queryset=GroupMember.objects.all())
            ).get(pk=pk)
        # Same cluster: can see public groups memberships
        elif request.user.has_common_cluster(user):
            user = User.objects.all().select_related('photo').prefetch_related(
                'clusters',
                Prefetch('memberships', queryset=GroupMember.objects.filter(Q(group__private=False) | Q(group__in=self.my_groups)).select_related('group'))
            ).get(pk=pk)
        # In the general case, we only see common Group memberships
        else:
            user = User.objects.all().select_related('photo').prefetch_related(
                'clusters',
                Prefetch('memberships', queryset=GroupMember.objects.filter(group__in=self.my_groups).select_related('group'))
            ).get(pk=pk)

        s = DetailedUserWithPermsSerializer(user, context={'request': request})
        return Response(s.data, status=status.HTTP_200_OK)

    def update(self, request, pk=None):
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
        response_serializer: DetailedUserWithPermsSerializer
        """
        if request.user.__class__.__name__ == 'AnonymousUser':
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        else:
            # Use DetailedUserWithPermsSerializer to have the groups whom user belongs to
            user = User.objects.all().select_related('photo').prefetch_related(
                Prefetch('memberships', queryset=GroupMember.objects.all().select_related('group'))
            ).get(pk=request.user.id)
            s = MyUserDetailsWithPermsSerializer(user, context={'request': request})
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

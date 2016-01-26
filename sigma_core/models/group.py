from django.db import models

from dry_rest_permissions.generics import allow_staff_or_superuser

from sigma_core.models.custom_field import CustomField
from sigma_core.models.group_field import GroupField


class Group(models.Model):
    class Meta:
        pass

    ADMINISTRATOR_RANK  = 10

    VIS_PUBLIC          = 'public'
    VIS_PRIVATE         = 'private'
    VISIBILITY_CHOICES = (
        (VIS_PUBLIC, 'Anyone can see the group'),
        (VIS_PRIVATE, 'Group is not visible')
    )

    TYPE_BASIC          = 'basic'
    TYPE_CURSUS         = 'cursus'
    TYPE_ASSO           = 'association'
    TYPE_PROMO          = 'school_promotion'
    TYPE_SCHOOL         = 'school'
    TYPE_CHOICES = (
        (TYPE_BASIC, 'Simple group'),
        (TYPE_CURSUS, 'Cursus or department'),
        (TYPE_ASSO, 'Association'),
        (TYPE_PROMO, 'School promotion'),
        (TYPE_SCHOOL, 'School')
    )

    name = models.CharField(max_length=254)
    visibility = models.CharField(max_length=64, choices=VISIBILITY_CHOICES, default=VIS_PRIVATE)
    type = models.CharField(max_length=64, choices=TYPE_CHOICES, default=TYPE_BASIC)

    # The permission a member has upon joining
    # A value of -1 means that no one can join the group.
    # A value of 0 means that anyone can request to join the group
    default_member_rank = models.SmallIntegerField(default=-1)
    # Invite new members on the group
    req_rank_invite = models.SmallIntegerField(default=1)
    # Remove a member from the group
    req_rank_kick = models.SmallIntegerField(default=ADMINISTRATOR_RANK)
    # Upgrade someone rank 0 to rank 1
    req_rank_accept_join_requests = models.SmallIntegerField(default=1)
    # Upgrade other users (up to $yourRank - 1)
    req_rank_promote = models.SmallIntegerField(default=ADMINISTRATOR_RANK)
    # Downgrade someone (to rank 1 minimum)
    req_rank_demote = models.SmallIntegerField(default=ADMINISTRATOR_RANK)
    # Modify group description
    req_rank_modify_group_infos = models.SmallIntegerField(default=ADMINISTRATOR_RANK)

    # Related fields:
    #   - invited_users (model User)
    #   - memberships (model UserGroup)
    #   - fields (model GroupField)
    # TODO: Determine whether 'memberships' fields needs to be retrieved every time or not...

    def can_anyone_join(self):
        return self.default_member_rank >= 0

    def __str__(self):
        return "%s (%s)" % (self.name, self.get_type_display())

    ################################################################
    # PERMISSIONS                                                  #
    ################################################################

    # Perms for admin site
    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    # Permissions
    @staticmethod
    def has_read_permission(request):
        """
        All groups are visible by default.
        """
        return True

    def has_object_read_permission(self, request):
        """
        Public groups are visible by everybody. Private groups are only visible by members.
        """
        return self.visibility == Group.VIS_PUBLIC or request.user.is_group_member(self)

    @staticmethod
    def has_write_permission(request):
        return True

    @staticmethod
    @allow_staff_or_superuser
    def has_create_permission(request):
        """
        Everybody can create a private group. For other types, user must be school admin or sigma admin.
        """
        #TODO: Adapt after School model implementation.
        group_type = request.data.get('type', None)
        return group_type == Group.TYPE_BASIC

    def has_object_write_permission(self, request):
        return False

    @allow_staff_or_superuser
    def has_object_update_permission(self, request):
        """
        Only group's admins and Sigma admins can edit a group.
        """
        return request.user.can_modify_group_infos(self)

    @allow_staff_or_superuser
    def has_object_invite_permission(self, request):
        return request.user.can_invite(self)

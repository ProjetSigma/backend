from django.db import models

from dry_rest_permissions.generics import allow_staff_or_superuser

from sigma_core.models.custom_field import CustomField
from sigma_core.models.group_field import GroupField


class Group(models.Model):
    #########################
    # Constants and choices #
    #########################
    ADMINISTRATOR_RANK = 10

    ##########
    # Fields #
    ##########
    name = models.CharField(max_length=254)
    is_private = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    is_protected = models.BooleanField(default=False) # if True, the Group cannot be deleted

    # The cluster responsible of the group in case of admin conflict (can be null for non-cluster-related groups)
    resp_group = models.ForeignKey('Group', null=True, blank=True, on_delete=models.SET_NULL)

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
    #   - memberships (model GroupMember)
    #   - users (model User)
    #   - fields (model GroupField)
    # TODO: Determine whether 'memberships' fields needs to be retrieved every time or not...

    @property
    def subgroups(self):
        return [ga.subgroup for ga in self.subgroups.filter(validated=True).select_related('subgroup')]

    @property
    def members_count(self):
        return self.memberships.count()

    #################
    # Model methods #
    #################
    def can_anyone_join(self):
        return self.default_member_rank >= 0

    def __str__(self):
        return self.name

    ###############
    # Permissions #
    ###############

    # Perms for admin site
    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    # DRY Permissions
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
        # Handled in View directly with queryset override
        return True

    @staticmethod
    def has_write_permission(request):
        return True

    @staticmethod
    @allow_staff_or_superuser
    def has_create_permission(request):
        """
        Everybody can create a group.
        """
        return True

    @allow_staff_or_superuser
    def has_object_write_permission(self, request):
        return request.user.has_group_admin_perm(self)

    @allow_staff_or_superuser
    def has_object_update_permission(self, request):
        """
        Only group's admins and Sigma admins can edit a group.
        """
        return request.user.can_modify_group_infos(self)


class GroupAcknowledgment(models.Model):
    subgroup = models.ForeignKey(Group, related_name='group_parents')
    parent_group = models.ForeignKey(Group, related_name='subgroups')
    validated = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.validated:
            return "Group %s acknowledged by Group %s" % (self.subgroup.__str__(), self.parent_group.__str__())
        else:
            return "Group %s awaiting for acknowledgment by Group %s since %s" % (self.subgroup.__str__(), self.parent_group.__str__(), self.created.strftime("%Y-%m-%d %H:%M"))

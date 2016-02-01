from django.db import models

from dry_rest_permissions.generics import allow_staff_or_superuser

# class GroupManager(models.Manager):
#     # TODO: Determine whether 'memberships' fields needs to be retrieved every time or not...
#     def get_queryset(self):
#         return super(GroupManager, self).get_queryset().prefetch_related('memberships')


class Group(models.Model):
    #########################
    # Constants and choices #
    #########################
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

    ##########
    # Fields #
    ##########
    name = models.CharField(max_length=254)
    visibility = models.CharField(max_length=64, choices=VISIBILITY_CHOICES, default=VIS_PRIVATE)
    type = models.CharField(max_length=64, choices=TYPE_CHOICES, default=TYPE_BASIC)

    # The school responsible of the group in case of admin conflict (can be null for non-school-related groups)
    resp_school = models.ForeignKey('School', null=True, blank=True, on_delete=models.SET_NULL)

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

    # objects = GroupManager()

    @property
    def acknowledged_groups(self):
        return [ga.asking_group for ga in self.group_acknowledgments.filter(validated=True).select_related('asking_group')]

    #################
    # Model methods #
    #################
    def can_anyone_join(self):
        return self.default_member_rank >= 0

    def __str__(self):
        return "%s (%s)" % (self.name, self.get_type_display())

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
        from sigma_core.models.school import School
        group_type = request.data.get('type', None)
        if group_type == Group.TYPE_BASIC:
            return True

        resp_school = request.data.get('resp_school', None)
        try:
            school = School.objects.get(pk=resp_school)
        except School.DoesNotExist:
            school = None
        return school is not None and request.user.has_group_admin_perm(school)

    @allow_staff_or_superuser
    def has_object_write_permission(self, request):
        return request.user.has_group_admin_perm(self)

    @allow_staff_or_superuser
    def has_object_update_permission(self, request):
        """
        Only group's admins and Sigma admins can edit a group.
        """
        return request.user.can_modify_group_infos(self)

    @allow_staff_or_superuser
    def has_object_invite_permission(self, request):
        return request.user.can_invite(self)


class GroupAcknowledgment(models.Model):
    asking_group = models.ForeignKey(Group, related_name='group_recognizers')
    validator_group = models.ForeignKey(Group, related_name='group_acknowledgments')
    validated = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.validated:
            return "Group %s acknowledged by Group %s" % (self.asking_group.__str__(), self.validator_group.__str__())
        else:
            return "Group %s awaiting for acknowledgment by Group %s since %s" % (self.asking_group.__str__(), self.validator_group.__str__(), self.created.strftime("%Y-%m-%d %H:%M"))

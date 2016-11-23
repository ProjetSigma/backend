from django.db import models


class Group(models.Model):
    #########################
    # Constants and choices #
    #########################

    CONF_PUBLIC = 0
    CONF_NORMAL = 1
    CONF_SECRET = 2

    ##########
    # Fields #
    ##########
    name = models.CharField(max_length=254)
    is_private = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    is_protected = models.BooleanField(default=False) # if True, the Group cannot be deleted
    can_anyone_ask = models.BooleanField(default=False) #if True, people don't need invitation to ask to join
    need_validation_to_join = models.BooleanField(default=False) #if True, people from the group who can invite need to accept the asker

    """ Set the confidentiality of the group's members
        If set to :
            CONF_PUBLIC -> The group is public (all members can be seen)
            CONF_NORMAL -> The group is normal (all members that I am connected to can be seen)
            CONF_SECRET -> The group is private (only the members can see themselves) """
    confidentiality = models.PositiveSmallIntegerField(default=CONF_NORMAL)


    # Related fields:
    #   - invited_users (model User)
    #   - memberships (model GroupMember)
    #   - users (model User)
    #   - fields (model GroupField)
    #   - subgroups (model Group)
    #   - group_parents (model Group)
    # TODO: Determine whether 'memberships' fields needs to be retrieved every time or not...

    @property
    def subgroups_list(self):
        return [ga.subgroup for ga in self.subgroups.filter(validated=True).select_related('subgroup')]

    @property
    def group_parents_list(self):
        return [ga.parent_group for ga in self.group_parents.filter(validated=True).select_related('parent_group')]

    @property
    def members_count(self):
        return self.memberships.count()

    #################
    # Model methods #
    #################

    def __str__(self): # pragma: no cover
        return self.name

    ###############
    # Permissions #
    ###############

    # Perms for admin site
    def has_perm(self, perm, obj=None): # pragma: no cover
        return True

    def has_module_perms(self, app_label): # pragma: no cover
        return True


class GroupAcknowledgment(models.Model):
    subgroup = models.ForeignKey(Group, related_name='group_parents')
    parent_group = models.ForeignKey(Group, related_name='subgroups')
    validated = models.BooleanField(default=False)
    delegate_admin = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self): # pragma: no cover
        if self.validated:
            return "Group %s acknowledged by Group %s" % (self.subgroup.__str__(), self.parent_group.__str__())
        else:
            return "Group %s awaiting for acknowledgment by Group %s since %s" % (self.subgroup.__str__(), self.parent_group.__str__(), self.created.strftime("%Y-%m-%d %H:%M"))

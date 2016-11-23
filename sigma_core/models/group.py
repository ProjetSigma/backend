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

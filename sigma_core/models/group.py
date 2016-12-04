from django.db import models
from sigma_core.models.user import User
from sigma_core.models.group_member import GroupMember

class Group(models.Model):
    #########################
    # Constants and choices #
    #########################

    POSSIBLE_CONF = (
        (0, 'Public'),
        (1, 'Normal'),
        (2, 'Secret'),
    )

    ##########
    # Fields #
    ##########
    name = models.CharField(max_length=254)
    description = models.TextField(blank=True)
    is_protected = models.BooleanField(default=False) # if True, the Group cannot be deleted
    can_anyone_ask = models.BooleanField(default=True) #if True, people don't need invitation to ask to join
    need_validation_to_join = models.BooleanField(default=False) #if True, people from the group who can invite need to accept the asker

    """ Set the confidentiality of the group's members
        If set to :
            CONF_PUBLIC -> The group is public (all members can be seen)
            CONF_NORMAL -> The group is normal (all members that I am connected to can be seen)
            CONF_SECRET -> The group is private (only the members can see themselves) """
    user_confidentiality = models.PositiveSmallIntegerField(choices=POSSIBLE_CONF, default=0)

    """Set the visibility
        If set to :
            CONF_PUBLIC -> The group can be seen by everyone
            CONF_NORMAL -> The group can be seen by people from acknowledged groups
            CONF_SECRET -> The group can be seen only by people who are in it """
    visibility = models.PositiveSmallIntegerField(choices=POSSIBLE_CONF,default=0)

    # Related fields:
    #   - invited_users (model User)
    #   - memberships (model GroupMember)
    #   - users (model User)
    #   - fields (model GroupField)
    #   - subgroups (model Group)
    #   - group_parents (model Group)
    # TODO: Determine whether 'memberships' fields needs to be retrieved every time or not...

    # WAS USED IN THE FRONT BUT WE MIGHT CHANGE IT
    # @property
    # def subgroups_list(self):
    #     return [ga.subgroup for ga in self.subgroups.filter(validated=True).select_related('subgroup')]
    #
    # @property
    # def group_parents_list(self):
    #     return [ga.parent_group for ga in self.group_parents.filter(validated=True).select_related('parent_group')]
    #
    # @property
    # def members_count(self):
    #     return self.memberships.count()

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

    @staticmethod
    def has_read_permission(request):
        return True
    @staticmethod
    def has_write_permission(request):
        return True

    def has_object_read_permission(self, request):
        return True

    def has_object_update_permission(self, request):
        if not request.user.can_modify_group_infos(self):
            return False

    def has_object_destroy_permission(self, request):
        try:
            user_mship=GroupMember.all().get(user=request.user,group=self)
            return user_mship.is_super_administrator
        except GroupMember.DoesNotExist:
            return False

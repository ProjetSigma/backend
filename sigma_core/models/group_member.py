from django.db import models
from django.http import Http404

from sigma_core.models.user import User

class GroupMember(models.Model):
    """
    Modelize a membership relation between an User and a Group.
    """
    class Meta:
        unique_together = (("user", "group"),)

    user = models.ForeignKey('User', related_name='memberships')
    group = models.ForeignKey('Group', related_name='memberships')
    created = models.DateTimeField(auto_now_add=True)
    join_date = models.DateField(blank=True, null=True)
    leave_date = models.DateField(blank=True, null=True)

    # is_accepted = is in the group
    # is_accepted = models.BooleanField(default=False)

    # if super_administrator = True then is_administrator = True
    # administrators must have all the rights below
    is_administrator = models.BooleanField(default=False)
    is_super_administrator = models.BooleanField(default=False)
    can_invite = models.BooleanField(default=False)
    can_be_contacted = models.BooleanField(default=False)
    can_publish = models.BooleanField(default=False)
    can_kick = models.BooleanField(default=False)
    can_modify_group_infos = models.BooleanField(default=False)

    # Related fields:
    #   - field_values (model GroupFieldValue)

    def __str__(self):
        return "User \"%s\" in Group \"%s\"" % (self.user.__str__(), self.group.__str__())

    # Perms for admin site
    def has_perm(self, perm, obj=None): # pragma: no cover
        return True

    def has_module_perms(self, app_label): # pragma: no cover
        return True

    #give the rights if the user is an admin or a super_admin
    def save(self, *args, **kwargs):
        if self.is_super_administrator:
            self.is_administrator = True

        if self.is_administrator:
            self.can_invite = True
            self.can_publish = True
            self.can_kick = True
            self.can_modify_group_infos = True

        super(Model, self).save(*args, **kwargs)


    ################################################################
    # PERMISSIONS                                                  #
    ################################################################

    @staticmethod
    def has_read_permission(request):
        return True
    @staticmethod
    def has_write_permission(request):
        return True


    ################################################################
    ## Read permissions

    @staticmethod
    def has_list_permission(request):
        return True

    def has_object_retrieve_permission(self, request):
        try:
            if request.user.id == self.user.id:
                return True
            else:
                #here the user is the one who tries to access the GroupMember object
                mb = GroupMember.objects.get(group=self.group.id, user=request.user.id)
                return True #maybe we will have to change it
        except GroupMember.DoesNotExist:
            return False


    ################################################################
    ## Write permissions

    @staticmethod
    def has_create_permission(request):
        return False

    def has_object_update_permission(self, request):
        try:
            #Membership of the one who tries to update a GroupMember the other dude
            mb = GroupMember.objects.get(group=self.group.id,user=request.user.id)
            right_to_change = request.data.get('right_to_change', None)

            if self.is_administrator==True:
                return mb.is_super_administrator
            else:
                basic_rights = ["can_invite","can_kick","can_publish","can_be_contacted","can_modify_group_infos"]
                if right_to_change in basic_rights:
                    return mb.can_modify_basic_rights
                else:
                    return mb.is_super_administrator

        except GroupMember.DoesNotExist:
            return False
        except request.data.DoesNotExist:
            return False


    def has_object_destroy_permission(self, request):
        try:
            mb = GroupMember.objects.get(group=self.group.id,user=request.user.id)
            if mb.is_super_administrator and self.is_super_administrator: #then mb=self
                return false
            elif self.is_administrator: #only a super-admin can kick an admin
                return mb.is_super_administrator
            else:
                return mb.can_kick
        except GroupMember.DoesNotExist:
            return False

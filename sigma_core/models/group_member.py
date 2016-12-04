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


        super(GroupMember, self).save(*args, **kwargs)



    def can_modify_basic_rights(self, my_mship):
        #rights to become superadmin or admin are not concerned
        #self = membership that's going to be modified
        #my_mship is the membership of the user who wants to modify right

        if my_mship.is_super_administrator:
            return True

        if my_mship.is_administrator and (not self.is_administrator or my_ship==self):
            return True

        return False


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
            #Membership of the one who tries to update a GroupMember of the other dude
            mb = GroupMember.objects.get(group=self.group.id,user=request.user.id)

            #new status of the membership
            serializer = GroupMemberSerializer(data=request.data)

            if not serializer.is_valid:
                return False

            new_basic_rights = [serializer.can_invite,serializer.can_kick,serializer.can_publish, \
            serializer.can_be_contacted,serializer.can_modify_group_infos]
            previous_basic_rights = [self.can_invite,self.can_kick,self.can_publish,self.can_be_contacted, \
            self.can_modify_group_infos]

            if not mb.can_modify_basic_rights:
                for i in range(len(new_basic_rights)):
                    if new_basic_rights[i] != previous_basic_rights[i]:
                        return False

            if (serializer.is_administrator != self.is_administrator or \
            serializer.is_super_administrator != self.is_super_administrator) and \
            (not mb.is_super_administrator or (mb_is_super_administrator and self==mb)):
                return False
            return True

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

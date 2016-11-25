from django.db import models

from sigma_core.models.user import User
from sigma_core.models.group import Group
from sigma_core.models.group_member import GroupMember

class GroupInvitation(models.Model):

    ################################################################
    # FIELDS                                                       #
    ################################################################

    class Meta:
        unique_together = (("invitee", "group"),)

    group = models.ForeignKey('Group', related_name='invitations')
    invitee = models.ForeignKey('User', related_name='invitations')
    emmited_by_invitee = models.BooleanField(default=True) #if false -> emitted by the group
    date = models.DateTimeField(auto_now_add=True)


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
        return False

    def has_object_retrieve_permission(self, request):
        try:
            if request.user.id == self.invitee.id:
                return True
            else:
                mb = GroupMember.objects.get(group=self.group.id, user=request.user.id)
                return mb.can_invite
        except GroupMember.DoesNotExist:
            return False


    ################################################################
    ## Write permissions

    @staticmethod
    def has_create_permission(request):
        try:
            if request.data.get('emmited_by_invitee'):
                #check if the user who is connected is the invitee
                #and if the group can be asked this way
                group=request.data.get('group')
                return (request.data.get('invitee').id == request.user.id and group.can_anyone_ask)
            else:
                #here, the user is the one who created the invitation, not the invitee
                mb = GroupMember.objects.get(group=request.data.get('group'), user=request.user.id)
                return mb.can_invite
        except GroupMember.DoesNotExist:
            return False

    def has_object_confirm_permission(self, request):
        try:
            if self.emmited_by_invitee:
                #here check if the member who agree to the invitation sent by the invitee
                #has the right to add him to the group
                mb = GroupMember.objects.get(group=self.group.id, user=request.user.id)
                return mb.can_invite
            else:
                return request.user.id == self.invitee.id
        except GroupMember.DoesNotExist:
            return False

    def has_object_update_permission(self, request):
        return False

    def has_object_destroy_permission(self, request):
        #the people that can destroy the invitation are the invited,
        #and members of the group that have the adequate right

        if request.user.id==self.invitee.id:
            return True
        try:
            mb = GroupMember.objects.get(group=self.group.id, user=request.user.id)
            return mb.can_invite
        except GroupMember.DoesNotExist:
            return False

    #if not need_validation_to_join then the GroupMember is directly created
    def save(self, *args, **kwargs):
        if not need_validation_to_join:
            GroupMember.objets.create(user=new_member,group=group)
        else:
            super(GroupInvitation, self).save(*args, **kwargs)

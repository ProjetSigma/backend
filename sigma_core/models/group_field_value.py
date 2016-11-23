from django.db import models

from sigma_core.models.group_field import GroupField
from sigma_core.models.group_member import GroupMember
from sigma_core.models.user import User

class GroupFieldValue(models.Model):
    class Meta:
        unique_together = (("membership", "field"),)

    ################################################################
    # FIELDS                                                       #
    ################################################################
    
    membership = models.ForeignKey('GroupMember', related_name='field_values')
    field = models.ForeignKey('GroupField', related_name='+')
    value = models.TextField(blank=True)

    ################################################################
    # PERMISSIONS                                                  #
    ################################################################

    @staticmethod
    def has_read_permission(request):
        return True
    @staticmethod
    def has_write_permission(request):
        return True
    
    
    
    @staticmethod
    def __has_access_permission(user_id, group):
        if group.confidentiality == Group.CONF_PUBLIC:
            return True
            
        elif group.confidentiality == Group.CONF_NORMAL:
            return True # TODO : check if the user has a relation with the group, otherwise, return False
            
        elif group.confidentiality == Group.CONF_SECRET:
            try:
                GroupMember.objects.get(user=user_id, group=group.id)
                return True
            except GroupMember.DoesNotExist:
                return False
    
    @staticmethod
    def has_list_permission(request):
        return False
        
    def has_object_retrieve_permission(self, request):
        return GroupFieldValue.__has_access_permission(request.user.id, self.group)
        
    
    
        
    """ Must be either an Administrator, or the user himself (when the field is not protected) """
    @staticmethod
    def __has_write_permission(user_id, field_id, membership_id):
        try:
            field = GroupField.objects.get(id = field_id)
            group_mb = GroupMember.objects.get(id = membership_id)
            if group_mb.user.id == user_id:
                return (not field.protected) or group_mb.is_administrator
            else:
                user_mb = GroupMember.objects.get(user = user_id, group = group_mb.group)
                return user_mb.is_administrator
                
        except GroupMember.DoesNotExist:
            return False
        
    @staticmethod
    def has_create_permission(request):
        return GroupFieldValue.__has_write_permission(request.user.id, request.data['field'], request.data['membership'])
    
    def has_object_update_permission(self, request):
        return GroupFieldValue.__has_write_permission(request.user.id, self.field.id, self.membership.id)
        
    def has_object_destroy_permission(self, request):
        return GroupFieldValue.__has_write_permission(request.user.id, self.field.id, self.membership.id)

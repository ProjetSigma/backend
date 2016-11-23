from django.db import models

from sigma_core.models.group import Group
from sigma_core.models.group_member import GroupMember

class GroupField(models.Model):

    ################################################################
    # CONSTANTS                                                    #
    ################################################################
    
    TYPE_NUMBER = 0
    TYPE_STRING = 1
    TYPE_CHOICE = 2 
    TYPE_EMAIL = 3
    
    TYPES = (
        (TYPE_NUMBER, "Number"),
        (TYPE_STRING, "String"),
        (TYPE_CHOICE, "Choice"),
        (TYPE_EMAIL, "Email")
    )


    ################################################################
    # FIELDS                                                       #
    ################################################################
    
    group = models.ForeignKey('Group', related_name='fields')
    name = models.CharField(max_length=254)
    type = models.PositiveSmallIntegerField(default=TYPE_NUMBER, choices=TYPES)
    accept = models.TextField(default='', blank=True)
    protected = models.BooleanField(default=False)
    multiple_values_allowed = models.BooleanField(default=False)
    

    ################################################################
    # PERMISSIONS                                                  #
    ################################################################
    
    @staticmethod
    def has_read_permission(request):
        return True  
    @staticmethod
    def has_write_permission(request):
        return True
        
    # Can see fields if :
    #   - the group is public
    #   - the group is normal, and I have a connection to it 
    #   - the group is private, and I am a member of it         
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
        
    def has_object_retrieve_permission(self, request):
        return GroupField.__has_access_permission(request.user.id, self.group)
        
        
    # Check that the user is related to the group
    @staticmethod
    def has_list_permission(request):
        # if 'group' in request.data:
        #    gid = request.data['group']
        #    return request.user.is_related_to_group(gid)
        # return False
        return True
        
    
    
        
    # Must be a group Administrator to change/create fields
    @staticmethod
    def __has_admin_permission(user_id, group_id):
        try:
            group_mb = GroupMember.objects.get(user = user_id, group = group_id)
            return group_mb.is_administrator
        except GroupMember.DoesNotExist:
            return False
        
    @staticmethod
    def has_create_permission(request):
        return GroupField.__has_admin_permission(request.user.id, request.data.get('group'))
    
    def has_object_update_permission(self, request):
        return GroupField.__has_admin_permission(request.user.id, self.group)
        
    def has_object_destroy_permission(self, request):
        return GroupField.__has_admin_permission(request.user.id, self.group)

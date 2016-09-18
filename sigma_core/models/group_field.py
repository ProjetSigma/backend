from django.db import models
from django.core.exceptions import ValidationError

from sigma_core.models.group import Group
from sigma_core.models.group_member import GroupMember

class GroupField(models.Model):

    ################################################################
    # CONSTANTS                                                    #
    ################################################################
    
    TYPE_NUMBER = 0
    TYPE_STRING = 1
    TYPE_EMAIL = 2


    ################################################################
    # FIELDS                                                       #
    ################################################################
    
    group = models.ForeignKey('Group', related_name='fields')
    name = models.CharField(max_length=254)
    type = models.PositiveSmallIntegerField(default=TYPE_NUMBER)
    accept = models.TextField(default='')


    ################################################################
    # VALIDATORS                                                   #
    ################################################################
    
    @staticmethod
    def validate(type, accept, value):
        validators = [number_validator, string_validator, email_validator]
        validators[type](value, accept)
        
    @staticmethod
    def number_validator(value, accept):
        return True
        
    @staticmethod
    def string_validator(value, accept):
        return True
        
    @staticmethod
    def email_validator(value, accept):
        return True
    

    ################################################################
    # PERMISSIONS                                                  #
    ################################################################
    
    """ Can see fields if :
        - the group is public
        - the group is normal, and I have a connection to it 
        - the group is private, and I am a member of it 
        
        Can not see the complete list of fields, never """
        
    @staticmethod
    def has_bygroup_permission(request, group):
        if group.confidentiality == Group.CONF_PUBLIC:
            return True
        elif group.confidentiality == Group.CONF_SECRET:
            group_mb = GroupMember.objects.filter(user = request.user.id, group = group.pk).count()
            return group_mb > 0
        else:
            return True
    
    def has_object_read_permission(self, request):
        return GroupField.has_bygroup_permission(request, self.group)
        
    @staticmethod
    def has_read_permission(request):
        return False
    
    
        
    """ Must be a group Administrator to change/create fields """
    def has_object_write_permission(self, request):
        group_mb = GroupMember.objects.filter(user = request.user.id, group = self.group).values_list('is_administrator', flat=True)
        return group_mb != [] and group_mb[0]
        
    @staticmethod
    def has_write_permission(request):
        group_mb = GroupMember.objects.filter(user = request.user.id, group = request.data.group).values_list('is_administrator', flat=True)
        return group_mb != [] and group_mb[0]
        

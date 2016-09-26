from rest_framework import serializers
import re

from sigma_core.models.group_field import GroupField
from sigma_core.models.group import Group

class GroupFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupField
        read_only_fields = ('group')

    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all())
    


    ################################################################
    # VALIDATORS                                                   #
    ################################################################
    
    # "Acceptable values" field validator
    accept_field_regex = [
        re.compile(r'^((-?[0-9]+)?_(-?[0-9]+)?)?$'),
        None,
        None,
        re.compile(r'^(((@|\.)?(\w+.)*\w+ +)*((@|\.)?(\w+\.)*\w+))?$'),
    ]
    
    def validate(self, data):
        if GroupFieldSerializer.accept_field_regex[data['type']] == None or not 'accept' in data:
            return data
            
        if 'type' in data and GroupFieldSerializer.accept_field_regex[data['type']].match(data['accept']):
            return data
        else:
            raise serializers.ValidationError("Le format des valeurs acceptables n'est pas valable.")
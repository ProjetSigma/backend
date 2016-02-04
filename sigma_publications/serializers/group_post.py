from rest_framework import serializers

from sigma_core.models.group import Group
from sigma_publications.models.group_post import GroupPost
from sigma_publications.models.group_post import Publication

class GroupPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupPost

    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all())
    publication = serializers.PrimaryKeyRelatedField(queryset=Publication.objects.all())

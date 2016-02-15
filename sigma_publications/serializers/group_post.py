from rest_framework import serializers

from sigma_core.models.group import Group
from sigma_publications.models import GroupPost, Publication

class GroupPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupPost

    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all())
    publication = serializers.PrimaryKeyRelatedField(queryset=Publication.objects.all())

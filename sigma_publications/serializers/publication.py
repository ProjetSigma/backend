from rest_framework import serializers

from sigma_core.models.group import Group
from sigma_core.models.user import User
from sigma_publications.models.group_post import GroupPost
from sigma_publications.models.publication import Publication

class PublicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publication

    poster_group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all())
    poster_user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    title = serializers.CharField(max_length=255)
    body = serializers.CharField()

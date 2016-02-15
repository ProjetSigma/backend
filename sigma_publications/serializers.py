from rest_framework import serializers

from sigma_core.models.group import Group
from sigma_core.models.user import User
from sigma_publications.models import Publication, PublicationComment, GroupPost

class PublicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publication

    poster_group = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=Group.objects.all())
    poster_user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    text = serializers.CharField()


class PublicationCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publication

    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    publication = serializers.PrimaryKeyRelatedField(queryset=Publication.objects.all())

    comment = serializers.CharField()

    # Automatic fields:
    #   - created
    #   - updated


class GroupPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupPost

    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all())
    publication = serializers.PrimaryKeyRelatedField(queryset=Publication.objects.all())

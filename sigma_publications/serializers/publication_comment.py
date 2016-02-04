from rest_framework import serializers

from sigma_core.models.user import User
from sigma_publications.models.group_post import Publication

class PublicationCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publication

    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    publication = serializers.PrimaryKeyRelatedField(queryset=Publication.objects.all())

    comment = serializers.CharField()

    # Automatic fields:
    #   - created
    #   - updated

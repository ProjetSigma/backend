from rest_framework import serializers

from sigma_core.models.publication import Publication


class PublicationSerializer(serializers.ModelSerializer):
    """
    Serialize a Group without its relations with users.
    """
    class Meta:
        model = Publication

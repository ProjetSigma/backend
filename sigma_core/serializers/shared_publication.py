from rest_framework import serializers

from sigma_core.models.shared_publication import SharedPublication

class SharedPublicationSerializer(serializers.ModelSerializer):
    """
    Serialize an event.
    """
    class Meta:
        model = SharedPublication

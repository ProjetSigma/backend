from rest_framework import serializers

from sigma_core.models.participation import Participation

class ParticipationSerializer(serializers.ModelSerializer):
    """
    Serialize an event.
    """
    class Meta:
        model = Participation

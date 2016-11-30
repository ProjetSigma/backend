from rest_framework import serializers

from sigma_core.models.event import Event

class EventSerializer(serializers.ModelSerializer):
    """
    Serialize an event.
    """
    class Meta:
        model = Event

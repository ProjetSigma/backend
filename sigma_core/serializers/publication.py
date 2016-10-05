from rest_framework import serializers

from sigma_core.models.publication import Publication

from sigma_core.models.event import Event

class PublicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publication

    # On precise que la relation MonModel.group doit se traduire par la clef primaire de l'objet pointe
    related_event = serializers.PrimaryKeyRelatedField(queryset=Event.objects.all())

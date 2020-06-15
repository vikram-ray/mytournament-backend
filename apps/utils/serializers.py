from rest_framework import serializers
from .models import InvitedUser

class InvitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvitedUser
        fields = ('__all__')

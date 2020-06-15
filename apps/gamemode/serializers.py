from rest_framework import serializers
from .models import GameMode


class GameModeSerializer(serializers.ModelSerializer):
    """ Platform Serilizers """
    class Meta:
        model = GameMode
        fields = ('id','name', 'description', 'size')

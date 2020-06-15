from rest_framework import serializers
from .models import Game


class GameSerializer(serializers.ModelSerializer):
    """ Platform Serilizers """
    class Meta:
        model = Game
        fields = ('id','name','company','description')

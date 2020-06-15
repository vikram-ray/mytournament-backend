from rest_framework import serializers

from .models import Platform

class PlatformSerializer(serializers.ModelSerializer):
    """ Platform Serilizers """
    class Meta:
        model = Platform
        fields = ('id','name')

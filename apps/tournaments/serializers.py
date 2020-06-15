import json

from rest_framework import serializers
from sentry_sdk import capture_exception
from django.core.validators import validate_email

from .models import Tournament

class TournamentSerializerGet(serializers.ModelSerializer):
    """ Platform Serilizers """
    created_by = serializers.SerializerMethodField()
    game_mode = serializers.SerializerMethodField()
    game = serializers.SerializerMethodField()
    platform = serializers.SerializerMethodField()
    class Meta:
        model = Tournament
        fields = ('id','created_at','platform','game_mode','game','created_by','rules','prize',
                    'contact_info','title','organizer','description','size','total_participants','start','end',
                        'notifications','extra_fields','winner')
        extra_kwargs = {
            'total_participants':{'read_only':True}, 'notifications':{'read_only':True}
        }
    def get_created_by(self, obj):
        if obj.created_by:
            return {
                "name": obj.created_by.name,
                "id": obj.created_by.id
            }
        return ''

    def get_game(self, obj):
        if obj.game:
            return {
                "name": obj.game.name,
                "id": obj.game.id
            }
        return ''
        
    def get_game_mode(self, obj):
        if obj.game_mode:
            return {
                "name": obj.game_mode.name,
                "id": obj.game_mode.id
            }
        return ''
    
    def get_platform(self, obj):
        if obj.platform:
            return {
                "name": obj.platform.name,
                "id": obj.platform.id
            }
        return ''

class TournamentSerializer(serializers.ModelSerializer):
    """ Platform Serilizers """
    class Meta:
        model = Tournament
        fields = ('id','created_at','platform','game_mode','game','created_by','rules','prize',
                    'contact_info','title','organizer','description','size','total_participants','start','end',
                        'notifications','extra_fields','winner')
        extra_kwargs = {
            'total_participants':{'read_only':True}
        }
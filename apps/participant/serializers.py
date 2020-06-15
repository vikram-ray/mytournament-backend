from rest_framework import serializers
from .models import Participant


class ParticipantSerializerGet(serializers.ModelSerializer):
    """ Platform Serilizers """
    user = serializers.SerializerMethodField()
    class Meta:
        model = Participant
        fields = ('id','created_at','user','blocked','extra_fields')

    def get_user(self, obj):
        user = {
            "id": obj.user.id,
            "name": obj.user.name,
            "short_name": obj.user.get_short_name(),
            "username": obj.user.username
        }
        return user


class ParticipantSerializer(serializers.ModelSerializer):
    """ Platform Serilizers """
    class Meta:
        model = Participant
        fields = ('id','created_at','user', 'mytournament','blocked','extra_fields')

    

class MyParticipantSerializer(serializers.ModelSerializer):
    """ Platform Serilizers """
    mytournament = serializers.SerializerMethodField()
    class Meta:
        model = Participant
        fields = ('id', 'mytournament')

    def get_mytournament(self, obj):
        mytournament = {
            'id': obj.mytournament.id,
            "created_by": {
                "name": obj.mytournament.created_by.name,
                "id": obj.mytournament.created_by.id
            },
            "game": {
                "name": obj.mytournament.game.name,
                "id": obj.mytournament.game.id
            },
            "game_mode": {
                "name": obj.mytournament.game_mode.name,
                "id": obj.mytournament.game_mode.id
            },
            "platform": {
                "name": obj.mytournament.platform.name,
                "id": obj.mytournament.platform.id
            },
            "organizer": obj.mytournament.organizer,
            "size": obj.mytournament.size,
            "total_participants": obj.mytournament.total_participants,
            "start": obj.mytournament.start,
            "title": obj.mytournament.title,            
        }
        return mytournament
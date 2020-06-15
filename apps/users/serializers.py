import json

from rest_framework import serializers
from apps.users import models
from apps.participant.models import Participant
from apps.tournaments.models import Tournament
from sentry_sdk import capture_exception
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .utils import get_safe_extra_fields

class CustomUserSerilizer(serializers.ModelSerializer):
    """ Custom User Serilizers """
    organized = serializers.SerializerMethodField()
    participated = serializers.SerializerMethodField()
    class Meta:
        model = models.CustomUser
        fields = ('id','mobile','username','email','name','password','created_at','extra_fields',
            'notifications','is_partner','about','last_login','participated','organized')
        extra_kwargs = {
            'password': {
                 'write_only': True,
                 'style': {'input_type': 'password'}
            }
        }

    def get_organized(self, obj):
        organized_data = Tournament.objects.filter(created_by=obj.id).count()
        return organized_data

    def get_participated(self, obj):
        participated = Participant.objects.filter(user=obj.id).count()
        return participated


    def create(self, validated_data):
        """ OverWriting default 'create' to use create_user to create a new user
            and save hashed password and return a new Profile User """

        user = models.CustomUser.objects.create_user(
            name=validated_data['name'],
            password=validated_data['password'],
            mobile=validated_data['mobile'],
            username=validated_data['username'],
        )
        return user

    def update(self, instance, validated_data):
        if 'password' in validated_data:
            instance.set_password(validated_data['password'])
            instance.save()
            return instance
        instance.name = validated_data.get('name', instance.name)
        if 'email' in validated_data:
            email = validated_data.get('email')
            if email=="":
                instance.email = None
            else:
                try:
                    validate_email(email)
                    instance.email = email
                except ValidationError as error:
                    capture_exception(error)
        instance.username = validated_data.get('username', instance.username)
        instance.about = validated_data.get('about', instance.about)
        if 'extra_fields' in validated_data:
            instance.extra_fields.update(get_safe_extra_fields(validated_data['extra_fields']))
        # if 'notifications' in validated_data:
        #     instance.notifications.update(validated_data['notifications'])
        extra_fields = validated_data.get('extra_fields', instance.extra_fields)
        instance.save()
        return instance


class CustomUserSerilizerList(serializers.ModelSerializer):
    """ Custom User Serilizers """
    organized = serializers.SerializerMethodField()
    participated = serializers.SerializerMethodField()
    class Meta:
        model = models.CustomUser
        fields = ('id','username','email','name','password','created_at','is_partner','about','last_login','participated','organized')
        extra_kwargs = {
            'password': {
                 'write_only': True,
                 'style': {'input_type': 'password'}
            }
        }

    def get_organized(self, obj):
        organized_data = Tournament.objects.filter(created_by=obj.id).count()
        return organized_data

    def get_participated(self, obj):
        participated = Participant.objects.filter(user=obj.id).count()
        return participated


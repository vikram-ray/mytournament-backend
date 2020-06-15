from django.db import models
from django.contrib.postgres.fields import ArrayField, JSONField

from apps.utils.models import MyBaseModel
from apps.users.models import CustomUser
from apps.tournaments.models import Tournament

class Participant(MyBaseModel):
    """ Participant model"""
    mytournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    extra_fields = JSONField(null=True,blank=True, default=dict)
    blocked = models.BooleanField(default=False)

    class Meta:
        ordering = ["created_at"]
        verbose_name_plural = 'Participants'

    def __str__(self):
        return self.mytournament.title
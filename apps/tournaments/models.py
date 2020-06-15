from django.db import models
from django.contrib.postgres.fields import ArrayField, JSONField

from apps.utils.models import MyBaseModel
from apps.users.models import CustomUser
from apps.platform.models import Platform
from apps.game.models import Game
from apps.gamemode.models import GameMode


class Tournament(MyBaseModel):
    """ Tournament Model """
    platform = models.ForeignKey(Platform,on_delete=models.PROTECT)
    game_mode = models.ForeignKey(GameMode,on_delete=models.PROTECT)
    game = models.ForeignKey(Game, on_delete=models.PROTECT)
    created_by = models.ForeignKey(CustomUser, on_delete=models.PROTECT, related_name='created_by')

    rules = models.CharField(max_length=2048, blank=True, null=True)
    prize = models.CharField(max_length=512, blank=True, null=True)
    contact_info = models.CharField(max_length=256, blank=True, null=True)
    title = models.CharField(max_length=64)
    winner = models.CharField(max_length=20, null=True, blank=True, default=None)
    organizer = models.CharField(max_length=30)
    description = models.CharField(max_length=2048)

    size = models.IntegerField()
    total_participants = models.IntegerField(default=0)

    start = models.DateTimeField()
    end = models.DateTimeField(null=True, blank=True, default=None)

    notifications = ArrayField(models.CharField(max_length=128), blank=True, null=True)

    extra_fields = JSONField(null=True, blank=True, default=dict)

    class Meta:
        ordering = ["start"]
        verbose_name_plural = 'Tournaments'

    def __str__(self):
        return self.organizer + " -> " + self.title

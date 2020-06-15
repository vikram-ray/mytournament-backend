from django.db import models


class GameMode(models.Model):
    """ Game Mode """
    name = models.CharField(max_length=32, unique=True)
    description = models.CharField(max_length=128)
    size = models.IntegerField()

    class Meta:
        ordering = ["name"]
        verbose_name_plural = 'Game Modes'

    def __str__(self):
        return self.name

from django.db import models

class Game(models.Model):
    """ Game Model """
    name = models.CharField(max_length=64)
    company = models.CharField(max_length=64)
    description = models.CharField(max_length=128)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = 'Games'

    def __str__(self):
        return self.name


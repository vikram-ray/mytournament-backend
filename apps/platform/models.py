from django.db import models

class Platform(models.Model):
    name = models.CharField(max_length=32)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = 'Platforms'

    def __str__(self):
        return self.name

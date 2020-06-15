import uuid
from django.core.validators import  RegexValidator

from django.db import models
# Create your models here.


class MyBaseModel(models.Model):
    """ Default Basemodel of the project to give id, created_at, updated_at"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True



onlynumeric = RegexValidator(regex=r'^\+?1?\d{10,10}$', message="Phone number must be 10 digit")
unique_mobile_error = {
    'unique': ("This mobile number is already invited"),
        }
class InvitedUser(MyBaseModel):
    mobile = models.CharField(max_length=10, unique=True, validators=[onlynumeric],error_messages=unique_mobile_error)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = 'InvitedUsers'

    def __str__(self):
        return self.mobile

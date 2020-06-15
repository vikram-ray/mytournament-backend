import uuid, json

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager
from django.core.validators import MinLengthValidator, RegexValidator
from django.conf import settings
from django.contrib.postgres.fields import JSONField, ArrayField
from sentry_sdk import capture_exception

from apps.utils.constants import SMS_CREDIT

alphanumeric = RegexValidator(r'^[0-9a-zA-Z]*$', 'Only alphanumeric characters are allowed.')
onlynumeric = RegexValidator(regex=r'^\+?1?\d{10,10}$', message="Phone number must be 10 digit")
error_message = {
    'unique': ("A user with that username already exists."),
        }
unique_mobile_error = {
    'unique': ("A mytournament user with that mobile already exists. If it is you please login."),
        }
initial_extra_fields = {
        SMS_CREDIT: int(settings.SMS_CREDIT),
    }


"""
    by default all models have manager class i.e. YOURMODEL.objects is defailt manager for all model
"""
class CustomUserManager(UserManager):
    """ Custom manager Model """
    def create_user(self, mobile, username, name, password=None):
        if not mobile:
            raise ValueError('You Must Provide an Mobile Number')
        user = self.model(name=name, mobile=mobile, username=username, extra_fields = initial_extra_fields)
        user.set_password(password)     
        user.save(using=self._db)
        return user

    def create_superuser(self, mobile, username, name, password=None):
        """ Create a superUser , is_superuser comes from PermissionMixins , is_staff is required"""
        user = self.create_user(mobile,username, name,  password)
        user.is_superuser = True
        user.is_staff = True
        user.save()
        return user

class CustomUser(AbstractBaseUser, PermissionsMixin):
    """ This is custom user model ,add this in setting AUTH_USER_MODEL='apps...' """
    """ mobile, firstname, username is requieed """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True) 
    mobile = models.CharField(max_length=10, unique=True, validators=[onlynumeric],error_messages=unique_mobile_error)
    username = models.CharField(max_length=20, unique=True, validators=[alphanumeric,MinLengthValidator(3)],error_messages=error_message)
    name = models.CharField(max_length=128)
    about = models.CharField(max_length=1024, default=None, null=True, blank=True)
    email = models.EmailField(max_length=128, blank=True, null=True, default=None)
    notifications = ArrayField(models.CharField(max_length=128), blank=True, null=True, default=list)
    extra_fields = JSONField(null=True,blank=True, default=dict)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_partner = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'mobile'
    REQUIRED_FIELDS = ['name', 'username']
    
    def get_short_name(self):
        if self.name:
            name = self.name.split()
            if len(name) > 0:
                return name[0]
        return '' 

    def __str__(self):
        view = '{0} - {1}'.format(self.name, self.mobile)
        if self.email:
            view += " - " + str(self.email)
        return view

    # def delete(self, *args, **kwargs):
    #     return vikram
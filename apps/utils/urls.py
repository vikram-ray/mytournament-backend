from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import InvitationViewset, GroupInvitationViewset, Notification

router = DefaultRouter()
router.register('invite',InvitationViewset, basename='invited_user')
router.register('groupinvite',GroupInvitationViewset, basename='group')
router.register('notification',Notification, basename='group')

urlpatterns = [
    path('', include(router.urls))
]
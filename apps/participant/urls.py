from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.participant import views

router = DefaultRouter()
router.register('',views.ParticipantViewset, basename='participant')

urlpatterns = [
    path('', include(router.urls))
]
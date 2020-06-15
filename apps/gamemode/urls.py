from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.gamemode import views

router = DefaultRouter()
router.register('',views.GameModeViewset, basename='gamemode')

urlpatterns = [
    path('', include(router.urls))
]
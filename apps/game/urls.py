from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.game import views

router = DefaultRouter()
router.register('',views.GameViewset, basename='game')

urlpatterns = [
    path('', include(router.urls))
]
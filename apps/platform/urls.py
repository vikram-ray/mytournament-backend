from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.platform import views

router = DefaultRouter()
router.register('',views.PlatformViewset, basename='platform')

urlpatterns = [
    path('', include(router.urls))
]
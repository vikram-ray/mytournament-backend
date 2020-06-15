from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.tournaments import views

router = DefaultRouter()
router.register('',views.TournamentViewset, basename='tournament')

urlpatterns = [
    path('', include(router.urls))
]
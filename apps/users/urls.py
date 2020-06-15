from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.users import views

router = DefaultRouter()
router.register('',views.CustomUserViewset)

urlpatterns = [
    path('login/', views.CustomUserLoginApiView.as_view()),
    path('', include(router.urls))
]
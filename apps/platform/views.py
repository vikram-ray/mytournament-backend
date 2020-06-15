from rest_framework import viewsets

from .models import Platform
from .serializers import PlatformSerializer
from apps.utils.permissions import CustomReadonlyPermission

class PlatformViewset(viewsets.ModelViewSet):
    """ List viewset from Platfor """
    queryset = Platform.objects.all()
    serializer_class = PlatformSerializer
    permission_classes = (CustomReadonlyPermission,)
    model = Platform

from rest_framework import viewsets

from .models import GameMode
from .serializers import  GameModeSerializer
from apps.utils.permissions import CustomReadonlyPermission

class GameModeViewset(viewsets.ModelViewSet):
    """ List viewset from Platfor """
    queryset = GameMode.objects.all()
    serializer_class = GameModeSerializer
    permission_classes = (CustomReadonlyPermission,)
    model = GameMode



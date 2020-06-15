from rest_framework import viewsets

from .models import Game
from .serializers import GameSerializer
from apps.utils.permissions import CustomReadonlyPermission

class GameViewset(viewsets.ModelViewSet):
    """ List viewset from Platfor """
    queryset = Game.objects.all()
    serializer_class = GameSerializer
    permission_classes = (CustomReadonlyPermission,)
    model = Game


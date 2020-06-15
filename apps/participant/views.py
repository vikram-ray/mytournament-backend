from rest_framework import viewsets

from .models import Participant
from .serializers import ParticipantSerializer
from apps.utils.permissions import CustomReadonlyPermission


class ParticipantViewset(viewsets.ModelViewSet):
    """ List viewset from Platfor """
    queryset = Participant.objects.all()
    serializer_class = ParticipantSerializer
    permission_classes = (CustomReadonlyPermission,)
    model = Participant

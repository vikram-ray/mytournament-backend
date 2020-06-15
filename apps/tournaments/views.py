import datetime

from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action

from sentry_sdk import capture_exception, capture_message
from .models import Tournament
from .serializers import TournamentSerializer, TournamentSerializerGet
from .permissions import TournamentUpdatePermission
from apps.utils.permissions import CustomReadonlyPermission

from apps.users.models import CustomUser
from apps.platform.models import Platform
from apps.game.models import Game
from apps.gamemode.models import GameMode
from apps.participant.models import Participant
from apps.participant.serializers import ParticipantSerializer, ParticipantSerializerGet, MyParticipantSerializer

class TournamentViewset(viewsets.ModelViewSet):
    """ List viewset from Platfor """
    queryset = Tournament.objects.all()
    queryset_past = Tournament.objects.filter(start__lte=datetime.datetime.now())
    queryset_upcoming = Tournament.objects.filter(start__gte=datetime.datetime.now())
    serializer_class = TournamentSerializer
    serializer_class_get = TournamentSerializerGet
    permission_classes = [IsAuthenticated,]
    model = Tournament

    def get_permissions(self):
        permission_classes = [AllowAny]
        if self.action in ['participate','mytournament','myparticipation']:
            permission_classes = [IsAuthenticated]
        elif self.action in ['notification']:
            permission_classes = [IsAuthenticated,TournamentUpdatePermission, ]
        elif self.request.method == 'POST':
            permission_classes = [IsAuthenticated]
        if self.request.method in ['PATCH','DELETE']:
            permission_classes = [IsAuthenticated,TournamentUpdatePermission, ]
        return [permission() for permission in permission_classes]   
    

    def list(self, request):
        """ List all tournament """
        try:
            past = request.GET.get('past')
            if past == 'true':
                queryset = self.filter_queryset(self.queryset_past)
            else:
                queryset = self.filter_queryset(self.queryset_upcoming)
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.serializer_class_get(page, many=True)
                return self.get_paginated_response(serializer.data)
            serializer = self.serializer_class_get(queryset, many=True)
            return Response(serializer.data)     

            context = {"success": True, "data": serializer.data}
            return Response(context, status=status.HTTP_200_OK)
        except Exception as error:
            capture_exception(error)
            context = {"success": False,"error": str(error), "message":"Error occured in tournament"}
            return Response(context, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def create(self, request):
        """ Create tournament """
        try:
            request_data = request.data.copy()
            request_data['created_by'] = request.user.id
            serializer = self.get_serializer(data=request_data)
            if serializer.is_valid():
                obj = self.perform_create( serializer)
                context = {"success": True, "data":serializer.data}
                capture_message('{},{},{} just created a tournament'.format(request.user.mobile, request.user.name, request.user.username))
                return Response(context, status=status.HTTP_200_OK)
            else:
                context = {"success": False, "error": str(serializer.errors), "message": "Tournament cannot be added"}
                return Response(context, status=status.HTTP_400_BAD_REQUEST)
        except Exception as error:
            capture_exception(error)
            context = {"success": False, "error": str(error), "message":"Tournament cannot be added at the moment"}
            return Response(context, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def retrieve(self, request, pk=None):
        """ Get a  tournament """
        try:
            obj = self.get_object()
            context = {"success":True, "data": self.serializer_class_get(obj).data}
            return Response(context, status=status.HTTP_200_OK)
        except Exception as error:
            capture_exception(error)
            context = {"success": False,"error": str(error), "message":"Error occured in getting tournament"}
            return Response(context, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def partial_update(self, request, pk):
        """ Update a tournament """
        try:
            obj = self.get_object()
            request_data = request.data.copy()
            if 'created_by' in request_data:
                request_data.pop('created_by')
            serializer = self.get_serializer(obj, data=request_data, partial=True)
            if serializer.is_valid():
                self.perform_update( serializer)
                context = {"success": True, "data":serializer.data}
                return Response(context, status=status.HTTP_200_OK)
            else:
                context = {"success": False, "error": str(serializer.errors), "message": "Tournament cannot be updated "}
                return Response(context, status=status.HTTP_400_BAD_REQUEST)
        except Exception as error:
            capture_exception(error)
            context = {"success": False, "error": str(error), "message":"Tournament cannot be updated at the moment"}
            return Response(context, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def destroy(self, request, pk=None):
        """ List all tournament """
        try:
            obj = self.get_object()
            capture_message('{0} is going to delete {1}'.format(request.user.mobile, str(obj)))
            if obj.total_participants > 0:
                context = {"success": True, "message": "Some users are already registered so you cannot delete this tournament"}
                return Response(context, status=status.HTTP_400_BAD_REQUEST)

            self.perform_destroy(obj)
            context = {"success": True, "message": "Tournament deleted successfully"}
            return Response(context, status=status.HTTP_200_OK)
        except Exception as error:
            capture_exception(error)
            context = {"success": False, "error": str(error), "message":"Cannot delete Tournament"}
            return Response(context, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, pk):
        """ Update a tournament """
        context = {"success": False,"error": True, "Message":"This method is not allowed"}
        return Response(context, status=status.HTTP_405_METHOD_NOT_ALLOWED)


    @action(detail=True, methods=['get'])
    def participant(self, request, pk):
        """ Get all participant """
        try:
            participants = Participant.objects.filter(mytournament__exact=pk)
            page = self.paginate_queryset(participants)
            if page is not None:
                serializer = ParticipantSerializerGet(page, many=True)
                data = self.get_paginated_response(serializer.data).data
                context = {"message":"participant data returned successfully ", "data": data}
                if request.user.is_authenticated:
                    participated = Participant.objects.filter(mytournament__exact=pk, user__exact=request.user.id)
                    if participated.exists():
                        context['participated'] = True
                    else:
                        context['participated'] = False
                return Response(context, status=status.HTTP_200_OK)
            serializer = ParticipantSerializerGet(participants, many=True)
            return Response(serializer.data)     

        except Exception as error:
            capture_exception(error)
            context = {"success": False,"error": str(error), "message":"Error occured in tournament"}
            return Response(context, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    @action(detail=True, methods=['post'])
    def participate(self, request, pk):
        """ participate a new user """
        try:
            tournament = self.get_object()
            participant = Participant.objects.filter(mytournament__exact=pk, user__exact=request.user.id)
            if participant.exists():
                context = {"success": False, "message":"You are already registered in the tournament"}
                return Response(context, status=status.HTTP_400_BAD_REQUEST)
            if(not tournament.size > tournament.total_participants):
                context = {"success": False, "message":"No slot is available in this tournament"}
                return Response(context, status=status.HTTP_400_BAD_REQUEST)
            serializer = ParticipantSerializer(data={"mytournament":pk, "user":request.user.id})
            if serializer.is_valid():
                obj = serializer.save()
                tournament.total_participants = tournament.total_participants + 1
                tournament.save()
                data = {
                    'name': obj.user.name,
                    'mytournament': obj.mytournament.title
                }
                context = {"success": True, "data":data, "message": "You have been registered"}
                return Response(context, status=status.HTTP_200_OK)
            else:
                context = {"success": False, "error": str(serializer.errors), "message": "Sorry, You cannot register right now."}
                return Response(context, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as error:
            capture_exception(error)
            context = {"success": False,"error": str(error), "message":"Error occured in tournament"}
            return Response(context, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



    @action(detail=True, methods=['post'])
    def notification(self, request, pk):
        """ Notify registered user """
        try:
            instance = self.get_object()
            message = request.data['message'][:110]
            capture_message('{},{} --> {}'.format(request.user.id, request.user.mobile, message))
            if instance.notifications:
                instance.notifications.append(message)
            else:
                instance.notifications = [message]
            instance.save()
            if len(instance.notifications) > 5:
                instance.notifications.pop(0)
                instance.save()
            participants = Participant.objects.filter(mytournament__exact=pk)
            message = instance.organizer + " :: "+ str(datetime.datetime.utcnow().timestamp()).split('.')[0] + " :: " + "(" + instance.title + ") " + message
            if participants.exists():
                for participant in participants:
                    notifications = participant.user.notifications
                    if notifications:
                        notifications.append(message)
                    else:
                        notifications = [message]
                    if notifications and len(notifications) > 20:
                        notifications.pop(0)
                    participant.user.notifications = notifications
                    participant.user.save()

                context = {"success": True, "message":"Notification sent to the registered user"}
                return Response(context, status=status.HTTP_200_OK)
            context = {"success": False, "message":"No users are registered yet"}
            return Response(context, status=status.HTTP_400_BAD_REQUEST)            
          
        except Exception as error:
            capture_exception(error)
            context = {"success": False,"error": str(error), "message":"Error occured in tournament"}
            return Response(context, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    @action(detail=False, methods=['get'])
    def mytournament(self, request):
        """ Get all tournament of a user """
        try:
            tournament = Tournament.objects.filter(created_by__exact=request.user).order_by('-created_at')
            page = self.paginate_queryset(tournament)
            if page is not None:
                serializer = TournamentSerializerGet(page, many=True)
                return self.get_paginated_response(serializer.data)
            serializer = TournamentSerializerGet(tournament, many=True)
            return Response(serializer.data)     

        except Exception as error:
            capture_exception(error)
            context = {"success": False,"error": str(error), "message":"Error occured in tournament"}
            return Response(context, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    @action(detail=False, methods=['get'])
    def myparticipation(self, request):
        """ Get all participation of a user """
        try:
            participations = Participant.objects.filter(user__exact=request.user.id)
            page = self.paginate_queryset(participations)
            if page is not None:
                serializer = MyParticipantSerializer(page, many=True)
                return self.get_paginated_response(serializer.data) 
            serializer = ParticipantSerializerGet(participants, many=True)
            return Response(serializer.data)
        except Exception as error:
            capture_exception(error)
            context = {"success": False,"error": str(error), "message":"Error occured in tournament"}
            return Response(context, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

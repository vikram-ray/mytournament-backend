import datetime
from rest_framework import mixins, viewsets, generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from sentry_sdk import capture_exception, capture_message
from .models import InvitedUser
from apps.users.models import CustomUser
from .serializers import InvitationSerializer
from .sms import send_short_sms, send_group_sms

from mytournament.settings import MYTOURNAMENT_URL
class InvitationViewset(generics.CreateAPIView, viewsets.GenericViewSet):
    """
    Create a model instance.
    """
    queryset = InvitedUser.objects.all()
    serializer_class = InvitationSerializer
    permission_classes = [IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        message = '''Hi, {} have just invited you to join MyTournament. You can participate or organize tournaments for free on {}'''.format(request.user.username, MYTOURNAMENT_URL)
        return send_group_sms([serializer.data['mobile']], message)
        # return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class GroupInvitationViewset(generics.CreateAPIView, viewsets.GenericViewSet):
    """
    send group notification
    """
    queryset = None
    serializer_class = None
    permission_classes = [IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        try:
            if request.user.is_superuser:
                mobiles = request.data['mobiles']
                message = request.data['message']
                context = {"success": True, "message":"Notification sent to all users"}
                return send_group_sms(mobiles, message)
            else:
                context = {"success": False, "message":"You are not eligible to use this endpoint"}
                return Response(context, status=status.HTTP_400_BAD_REQUEST)
        except Exception as error:
            context = {"success": False, "error": str(error)}
            return Response(context, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class Notification(generics.CreateAPIView, viewsets.GenericViewSet):
    """
    send notification to mytournament users
    """
    queryset = None
    serializer_class = None
    permission_classes = [IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        try:
            if request.user.is_superuser:
                message = request.data['message'][:250]
                message = 'MyTournament' + " :: "+ str(datetime.datetime.utcnow().timestamp()).split('.')[0]  + " :: " + message
                users = CustomUser.objects.all()
                for user in users:
                    notifications = user.notifications
                    if notifications:
                        notifications.append(message)
                    else:
                        notifications = [message]
                    if notifications and len(notifications) > 20:
                        notifications.pop(0)
                    user.notifications = notifications
                    user.save()
                context = {"success": True, "message":"Notification sent to all users"}
                return Response(context, status=status.HTTP_202_ACCEPTED)
            else:
                context = {"success": False, "message":"You are not eligible to use this endpoint"}
                return Response(context, status=status.HTTP_400_BAD_REQUEST)
        except Exception as error:
            context = {"success": False, "error": str(error)}
            return Response(context, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


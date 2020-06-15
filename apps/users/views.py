import json
import datetime

from rest_framework import viewsets, status
from rest_framework.authentication import TokenAuthentication
from rest_framework import filters
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny, IsAuthenticated
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from sentry_sdk import capture_exception, capture_message
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from apps.users import models, serializers
from apps.users.permissions import UpdateOwnProfile, ChangeUserPasswordPermission
from apps.utils.permissions import CustomReadonlyPermission
from apps.utils.sms import send_otp, verify_otp, resend_otp

from .models import CustomUser


class CustomUserViewset(viewsets.ModelViewSet):
    """ Viewset to handle Users"""
    serializer_class_all = serializers.CustomUserSerilizer
    serializer_class = serializers.CustomUserSerilizerList
    queryset = models.CustomUser.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (UpdateOwnProfile,IsAuthenticated)
    filter_backends = (filters.SearchFilter,) 
    search_fields = ('username', 'email','mobile')


    # def list(self, request):
    #     """ List all users """
    #     try:
    #         page = self.paginate_queryset(self.get_queryset())
    #         if page is not None:
    #             serializer = self.serializer_class_list(page, many=True)
    #             return self.get_paginated_response(serializer.data)
    #         serializer = self.serializer_class_list(queryset, many=True)
    #         return Response(serializer.data)     

    #         context = {"success": True, "data": serializer.data}
    #         return Response(context, status=status.HTTP_200_OK)
    #     except Exception as error:
    #         capture_exception(error)
    #         context = {"success": False,"error": str(error), "message":"Error occured in user"}
    #         return Response(context, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def get_permissions(self):
        permission_classes = [IsAuthenticated]
        if self.action in ['change_password']:
            permission_classes = [IsAuthenticated, ChangeUserPasswordPermission,]
        elif self.action in ['forgot_password','query_username','set_new_password','signup_otp','signup']:
            permission_classes = [AllowAny]
        elif self.request.method == 'GET':
            permission_classes = [AllowAny]    
        elif self.request.method in ['PATCH','DELETE']:
            permission_classes = [IsAuthenticated,UpdateOwnProfile, ]
        return [permission() for permission in permission_classes]   
    

    def retrieve(self, request, pk=None):
        """ Get a  user """
        try:
            obj = self.get_object()
            if obj.id == request.user.id:
                context = {"success":True, "data": self.serializer_class_all(obj).data}
            else:
                context = {"success":True, "data": self.get_serializer(obj).data}
            return Response(context, status=status.HTTP_200_OK)
        except Exception as error:
            capture_exception(error)
            context = {"success": False,"error": str(error), "message":"Error occured in getting user data"}
            return Response(context, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request):
        context = {"success": False,"error": True, "message":"This method is not allowed"}
        return Response(context, status=status.HTTP_405_METHOD_NOT_ALLOWED)
       


    @action(detail=False, permission_classes=[AllowAny])
    def query_username(self, request, pk=None):
        try:
            username = request.GET.get('username','')
            if username and len(username)<2:
                context = {"success": False, "message":"Username must be minimum of 3 letters"}
                return Response(context, status=status.HTTP_400_BAD_REQUEST)
            user_obj = CustomUser.objects.get(username__exact=username)
            context = {"success": True, "message":"A user with this username already exist"}
            return Response(context, status=status.HTTP_200_OK)
        except Exception as error:
            context = {"success": False, "message":"User with this username is not available"}
            return Response(context, status=status.HTTP_400_BAD_REQUEST)



    """ user can get otp via mobile, username. User can also resend otp """
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def forgot_password(self, request, pk=None):
        try:
            mobile = request.data.get('mobile')
            username = request.data.get('username')
            resend = request.data.get('resend')

            if not any([mobile, username]):
                context = {'success': False,'message': 'please enter either mobile or username','error': 'Missing mobile and username'}
                return Response(context, status=status.HTTP_400_BAD_REQUEST)
            try:
                if username:
                    message = 'username {0} is not associated with any mytournament account'.format(username)
                    user_obj = CustomUser.objects.get(username__exact=username)
                else:
                    message = ' Mobile {0} is not associated with any mytournament account'.format(mobile)
                    user_obj = CustomUser.objects.get(mobile__exact=mobile)
            except Exception as error:
                    capture_exception(error)
                    context = {'success': False,'message': message, error: str(error)}
                    return Response(context, status=status.HTTP_400_BAD_REQUEST)
            if resend:
                sms_response = resend_otp(user_obj.mobile)
            else:
                sms_response = send_otp(user_obj.mobile)

            if sms_response:
                context = {'success': True,'message': '{} ,Please enter OTP sent on your number {}'.format(user_obj.get_short_name(), user_obj.mobile)}
                return Response(context, status=status.HTTP_200_OK)
            else:
                context = {'success': False,'message': 'OTP can not be sent. Please contact us or Try again after sometimes.','error': str(error)}
                return Response(context, status=status.HTTP_503_SERVICE_UNAVAILABLE)                              
        except Exception as error:
            capture_exception(error)
            context = {'success': False,'message': 'OTP can not be sent. Please contact us or Try again after sometimes.','error': str(error)}
            return Response(context, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def set_new_password(self, request, pk=None):
        try:
            mobile = request.data.get('mobile')
            username = request.data.get('username')
            otp = request.data.get('otp')
            new_password = request.data.get('newPassword')

            mobile_or_username = mobile or username

            valid_request = all([mobile_or_username, otp, new_password]) and len(new_password)>7
            if not valid_request:
                capture_message('{0} entered invalid otp {1}, username {2}'.format(mobile, otp, username))
                context = {'success': False,'message': 'Please fill correct otp with your password','error': 'missing mobile. otp, newPassword, mewUser'}
                return Response(context, status=status.HTTP_400_BAD_REQUEST)
            try:
                if username:
                    message = 'username {0} is not associated with any mytournament account'.format(username)
                    user_obj = CustomUser.objects.get(username__exact=username)
                else:
                    message = 'Mobile {0} is not associated with any mytournament account'.format(mobile)
                    user_obj = CustomUser.objects.get(mobile__exact=mobile)
            except Exception as error:
                capture_exception(error)
                context = {'success': False,'message': message}
                return Response(context, status=status.HTTP_400_BAD_REQUEST) 
            verify_otp_response, verify_otp_message = verify_otp(user_obj.mobile, otp)
            if verify_otp_response:
                user_obj.set_password(new_password)
                user_obj.save()
                capture_message('Password changed for {}'.format(user_obj.mobile))
                context = {'success': True,'message': 'Password successfully changed for {}. Please login.'.format(user_obj.mobile)}
                return Response(context, status=status.HTTP_200_OK)                
            else:
                context = {'success': False,'message': verify_otp_message}
                return Response(context, status=status.HTTP_400_BAD_REQUEST)                
        except Exception as error:
            capture_exception(error)
            context = {
                'success': False,'message': 'Password Cannot be changed. Please contact us or Try again after sometimes.','error': str(error)}
            return Response(context, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, ChangeUserPasswordPermission,])
    def change_password(self, request, pk=None):
        try:
            try:
                user_obj = self.get_object()
            except Exception as error:
                capture_exception(error)
                context = {'success': False,'message': 'User Not Found'}
                return Response(context, status=status.HTTP_404_NOT_FOUND)
            new_password = request.data.get('newPassword')
            old_password = request.data.get('oldPassword')
            password_valid = new_password and len(new_password) > 7
            valid_old_password = user_obj.check_password(old_password)
            if not password_valid:
                context = {'success': False,'message': 'password must be more than 7 character'}
                return Response(context, status=status.HTTP_400_BAD_REQUEST)
            if not valid_old_password:
                context = {'success': False,'message': 'Invalid credentials'}
                return Response(context, status=status.HTTP_400_BAD_REQUEST)
            user_obj.set_password(new_password)
            user_obj.save()
            capture_message('Password changed for {}'.format(user_obj.mobile))
            context = {'success': True,'message': 'Password successfully changed for {}.'.format(user_obj.mobile)}
            return Response(context, status=status.HTTP_200_OK)                
        except Exception as error:
            capture_exception(error)
            context = {'success': False,'message': 'Password Cannot be changed. Please contact us or Try again after sometimes.','error': str(error)}
            return Response(context, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



    """ user can get otp via mobile, username. User can also resend otp """
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def signup_otp(self, request, pk=None):
        try:
            mobile = request.data.get('mobile')
            resend = request.data.get('resend')
            if not mobile:
                context = {'success': False,'message': 'please enter Your Mobile Number','error': 'Missing mobile'}
                return Response(context, status=status.HTTP_400_BAD_REQUEST)
            user_query = CustomUser.objects.filter(mobile = mobile)
            if user_query.exists():
                context = {'success': False,'message': '{} is already a MyTournament User, Please Login'.format(mobile),'error': 'Existing user'}
                return Response(context, status=status.HTTP_400_BAD_REQUEST)
            if resend:
                sms_response = resend_otp(mobile)
            else:
                sms_response = send_otp(mobile)
            if sms_response:
                context = {'success': True,'message': 'Please enter OTP sent on {}'.format(mobile)}
                return Response(context, status=status.HTTP_200_OK)
            else:
                context = {'success': False,'message': 'OTP can not be sent. Please contact us or Try again after sometimes.'}
                return Response(context, status=status.HTTP_503_SERVICE_UNAVAILABLE)                              
        except Exception as error:
            capture_exception(error)
            context = {'success': False,'message': 'OTP can not be sent. Please contact us or Try again after sometimes.','error': str(error)}
            return Response(context, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def signup(self, request, pk=None):
        try:
            mobile = request.data.get('mobile')
            username = request.data.get('username')
            otp = request.data.get('otp')
            password = request.data.get('password')

            valid_request = all([mobile, username, otp, password]) and len(password)>7
            if not valid_request:
                capture_message('{0} entered invalid otp {1}, username {2}'.format(mobile, otp, username))
                context = {'success': False,'message': 'Please fill correct otp with your password','error': 'missing mobile. otp, newPassword, mewUser'}
                return Response(context, status=status.HTTP_400_BAD_REQUEST)
            user_obj = CustomUser.objects.filter(mobile=mobile)
            user_obj_username = CustomUser.objects.filter(username=username)
            if user_obj.exists() or user_obj_username.exists():
                context = {'success': False, 'message': 'MyTournament Account already exist with this credentials. Please login.'}
                return Response(context, status=status.HTTP_400_BAD_REQUEST)
                
            verify_otp_response, verify_otp_message = verify_otp(mobile, otp)
            if verify_otp_response:
                serializer = self.serializer_class_all(data = request.data)
                if serializer.is_valid():
                    user = serializer.save()
                    context = {'success': True,'message': 'MyTournament Account Successfully Created with {}. Please login.'.format(mobile), 'data':serializer.validated_data}
                    return Response(context, status=status.HTTP_200_OK)
                else:
                    context = {'success': False,'message': 'Account Cannot be created at the moment.'}
                    return Response(context, status=status.HTTP_400_BAD_REQUEST)
            else:
                context = {'success': False,'message': verify_otp_message}
                return Response(context, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        except Exception as error:
            capture_exception(error)
            context = {
                'success': False,'message': 'OTP can not be Verified. Please contact us or Try again after sometimes.','error': str(error)}
            return Response(context, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CustomUserLoginApiView(ObtainAuthToken):
    """create auth token for users"""
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        user.last_login = datetime.datetime.now()
        user.save()
        return Response({'token': token.key, 'username':user.username, 'name': user.name, 'id':user.id})
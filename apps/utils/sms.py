import http.client
import json
import os
from rest_framework.response import Response
from rest_framework import status
from sentry_sdk import capture_exception, capture_message

from django.conf import settings

SMS_SENDER = settings.SMS_SENDER
SMS_PROVIDER_AUTH_KEY = settings.SMS_PROVIDER_AUTH_KEY
SMS_PROVIDER_BASE_URL = settings.SMS_PROVIDER_BASE_URL
SMS_ROUTE = settings.SMS_ROUTE
MSG91_SENDOTP_URL = '/api/sendotp.php?'
MSG91_VERIFYOTP_URL = '/api/verifyRequestOTP.php?'
MSG91_RESENDOTP_URL = '/api/retryotp.php?'

def send_otp(number):
    try:
        url = 'http://' + SMS_PROVIDER_BASE_URL + MSG91_SENDOTP_URL
        conn = http.client.HTTPSConnection(SMS_PROVIDER_BASE_URL)
        request_url = url + "authkey={authkey}&mobile={number}&sender={sender}".format(
            authkey=SMS_PROVIDER_AUTH_KEY,
            number=number,
            sender=SMS_SENDER,
        )
        conn.request("GET", request_url)
        res = conn.getresponse()
        data = res.read()
        response = json.loads(data.decode("utf-8"))
        if response['type'] != 'success':
            context = {"success": False, "message": ('Unable to send otp on {}'.format(number)), "error": response['message']}
            capture_message(json.dumps(context))
            return False
        else:
            context = {"success": True, "message": ("otp sent successfully on {}".format(number))}
            capture_message(json.dumps(context))
            return True

    except Exception as error:
        context = {"success": False, "message": ("otp cannot be sent."), "error": str(error)}
        capture_exception(error)
        return False


def verify_otp(number,otp):
    try:
        url = 'http://' + SMS_PROVIDER_BASE_URL + MSG91_VERIFYOTP_URL
        conn = http.client.HTTPSConnection(SMS_PROVIDER_BASE_URL)
        request_url = url + "authkey={authkey}&mobile={number}&otp={otp}".format(
            authkey=SMS_PROVIDER_AUTH_KEY,
            number=number,
            otp=otp,
        )
        conn.request("GET", request_url)
        res = conn.getresponse()
        data = res.read()
        response = json.loads(data.decode("utf-8"))
        context=None
        if response['type'] != 'success':
            if response['message'] == 'already_verified':                    
                context = {"success": False, "message": ('{} is already verified'.format(number)), "error": response['message']}
            elif response['message'] == 'otp_not_verified':
                context = {"success": False, "message": ('You have entered wrong otp for {}'.format(number)), "error": response['message']}
            else:
                context = {"success": False, "message": ('Please enter correct otp sent on {}'.format(number)), "error": response['message']}
            capture_message(json.dumps(context))
            return False, context['message']
        else:
            context = {"success": True, "message": ("Mobile number {} verified successfully.".format(number))}
            return True, context['message']
    except Exception as error:
        context = {"success": False, "message": ("otp cannot be verified"), "error": str(error)}
        capture_exception(error)
        return False, context['message']


def resend_otp(number):
    try:
        url = 'http://' + SMS_PROVIDER_BASE_URL + MSG91_RESENDOTP_URL
        conn = http.client.HTTPSConnection(SMS_PROVIDER_BASE_URL)
        request_url = url + "authkey={authkey}&mobile={number}&retrytype={retrytype}".format(
            authkey=SMS_PROVIDER_AUTH_KEY,
            number=number,
            retrytype='text',
        )
        conn.request("GET", request_url)
        res = conn.getresponse()
        data = res.read()
        response = json.loads(data.decode("utf-8"))
        context=None
        if response['type'] != 'success':
            context = {"success": False, "message": ('otp resend failed on {}'.format(number)), "error": response['message']}
            capture_message(json.dumps(context))
            return False
        else:
            context = {"success": True, "message": ("otp resend on {} successfully.".format(number))}
            return True

    except Exception as error:
        context = {"success": False, "message": ("otp cannot be resend"), "error": str(error)}
        capture_exception(error)
        return False





def send_short_sms(number,message):
    try:
        conn = http.client.HTTPSConnection(SMS_PROVIDER_BASE_URL)
        request_url = "/api/sendhttp.php?" + "mobiles={number}&authkey={authkey}&route={route}&sender={sender}&message={message}&country={country}".format(
            authkey=SMS_PROVIDER_AUTH_KEY,
            number=number,
            route=SMS_ROUTE,
            sender=SMS_SENDER,
            message=message,
            country='91'
        )
        conn.request("GET", request_url)
        res = conn.getresponse()
        data = res.read()
        context = { "success": True, "message": ("Sent successfully sent on {}".format(number))}
        capture_message(json.dumps(context))
        return Response(context, status=status.HTTP_200_OK)

    except Exception as error:
        context = {"success": False, "message": ("otp cannot be sent."), "error": str(error)}
        capture_exception(error)
        return Response(context, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def send_group_sms(mobiles,message):
    try:
        conn = http.client.HTTPSConnection(SMS_PROVIDER_BASE_URL)
        json_payload = { 
            "sender": SMS_SENDER,
            "route": SMS_ROUTE,
            "country": '91', 
            "sms": [ { "message": message, "to": mobiles } ] ,
            }

        payload = json.dumps(json_payload)
        headers = {
            'authkey': SMS_PROVIDER_AUTH_KEY,
            'content-type': "application/json"
            }
        conn.request("POST", '/api/v2/sendsms', payload, headers)
        res = conn.getresponse()
        data = res.read()
        response = json.loads(data.decode("utf-8"))
        if response['type'] != 'success':
            context = {"success": False, "message": ('We cannot send sms right now'), "error": response['message']}
            capture_message(json.dumps(context))
            return Response(context, status=status.HTTP_400_BAD_REQUEST)
        else:
            context = {"success": True, "message": ("sms sent successfully {}".format(mobiles))}
            capture_message(json.dumps(context))
            return Response(context, status=status.HTTP_200_OK)

    except Exception as error:
        context = {"success": False, "message": ("SMS cannot be sent."), "error":str(error)}
        capture_exception(error)
        return Response(context, status=status.HTTP_400_BAD_REQUEST)

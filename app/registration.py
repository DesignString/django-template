
import json

from decouple import config
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.tokens import default_token_generator
from rest_framework_simplejwt.tokens import RefreshToken

from django.db.models import Q
from rest_framework.decorators import api_view
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from app import models, serializers
from project_name import constants as const, utils


@swagger_auto_schema(method='post',
                     operation_id='signup',
                     operation_description="SignUp API",
                     request_body=openapi.Schema(
                                    type=openapi.TYPE_OBJECT,
                                    properties={
                                        'email': openapi.Schema(type=openapi.TYPE_STRING),
                                        'password': openapi.Schema(type=openapi.TYPE_STRING),
                                    }),
                     responses={
                         const.SUCCESS_STATUS_CODE: utils.swagger_data_response(
                             'Signed up successfully!',
                             {
                                 
                             })
                     })
@api_view(['POST'])
def signup(request):
    response = {}
    if request.method == 'POST':
        data = json.loads(request.body)
        if data.get('email', None) and data.get('password', None):
            user_exist = models.User.objects.filter(email=data.get('email')).first()
            if not user_exist:
                user = models.User.objects.create(
                    email=data.get('email'),
                    password=make_password(data.get('password')),
                    is_active=False
                )
                
                if user:
                    # trigger verification email
                    send_activation_email(user)
                    response['statusCode'] = const.SUCCESS_STATUS_CODE
                    response['message'] = 'Verification email sent successfully!'
                else:
                    response['statusCode'] = const.FAIL_STATUS_CODE
                    response['message'] = 'Unable to create user. Try again!'
            else:
                response['statusCode'] = const.ALREADY_EXIST_ERROR_CODE
                response['message'] = 'You have already registered. Please try to login!'
        else:
            response['statusCode'] = const.PARAMETER_MISSING_CODE
            response['message'] = const.PARAMETER_MISSING_OR_INVALID_MESSAGE
    else:
        response['statusCode'] = const.METHOD_NOT_ALLOWED_CODE
        response['message'] = 'Method not allowed!'
    return JsonResponse(response)

def get_activation_link(user):
    token = default_token_generator.make_token(user)
    link = '{}/emailverification/?token={}&email={}'.format(config('FRONTEND_URL'), token, user.email)
    return link

def send_activation_email(user):
    link = get_activation_link(user)
    context = {}
    context['link'] = link
    # Trigger activation email from here


def send_welcome_email(user):
    print(user)
    # Send welcome email from here
    

@swagger_auto_schema(method='post',
                     operation_id='emil_verification',
                     operation_description="Email Verification",
                     request_body=openapi.Schema(
                                    type=openapi.TYPE_OBJECT,
                                    properties={
                                        'email': openapi.Schema(type=openapi.TYPE_STRING),
                                        'token': openapi.Schema(type=openapi.TYPE_STRING),
                                    }),
                     responses={
                         const.SUCCESS_STATUS_CODE: utils.swagger_data_response(
                             'Email verified successfully!',
                             {
                                 'access': openapi.Schema(type=openapi.TYPE_STRING),
                                 'refresh': openapi.Schema(type=openapi.TYPE_STRING),
                                 'user': openapi.Schema(type=openapi.TYPE_OBJECT,
                                        properties={
                                            "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                                            "first_name": openapi.Schema(type=openapi.TYPE_STRING),
                                            "last_name": openapi.Schema(type=openapi.TYPE_STRING),
                                            "email": openapi.Schema(type=openapi.TYPE_STRING),
                                            "profile_pic": openapi.Schema(type=openapi.TYPE_STRING),
                                        }),
                             })
                     })
@api_view(['POST'])
def email_verification(request):
    response = {}
    if not request.body:
        response['statusCode'] = const.PARAMETER_MISSING_CODE
        response['message'] = const.PARAMETER_MISSING_MESSAGE
        return JsonResponse(response)
    data = json.loads(request.body)
    if data.get('token', None) and data.get('email', None):
        user = models.User.objects.filter(email=data.get('email')).first()
        if user:
            valid = default_token_generator.check_token(user, data.get('token'))
            if valid:
               
                response['message'] = 'Your email verified successfully!'
                user.is_active = 1
                user.save()
                
                send_welcome_email(user)
                
                response['data'] = {}
                response['data']['user'] = serializers.UserSerializer(user, many=False).data
                refresh = RefreshToken.for_user(user)
                response['data']['access'] = str(refresh.access_token)
                response['data']['refresh'] = str(refresh)
                response['statusCode'] = const.SUCCESS_STATUS_CODE
                
            else:
                response['statusCode'] = const.PARAMETER_VALIDATION
                response['message'] = 'Token is wrong/expired !'
        else:
            response['statusCode'] = const.USER_NOT_REGISTERED_CODE
            response['message'] = 'User not registered!'
    else:
        response['statusCode'] = const.PARAMETER_MISSING_CODE
        response['message'] = const.PARAMETER_MISSING_MESSAGE
    
    return JsonResponse(response)


@swagger_auto_schema(method='post',
                     operation_id='login',
                     operation_description="Login",
                     request_body=openapi.Schema(
                                    type=openapi.TYPE_OBJECT,
                                    properties={
                                        'email': openapi.Schema(type=openapi.TYPE_STRING),
                                        'password': openapi.Schema(type=openapi.TYPE_STRING),
                                    }),
                     responses={
                         const.SUCCESS_STATUS_CODE: utils.swagger_data_response(
                             'logged in successfully!',
                             {
                                 'access': openapi.Schema(type=openapi.TYPE_STRING),
                                 'refresh': openapi.Schema(type=openapi.TYPE_STRING),
                                 'user': openapi.Schema(type=openapi.TYPE_OBJECT,
                                        properties={
                                            "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                                            "first_name": openapi.Schema(type=openapi.TYPE_STRING),
                                            "last_name": openapi.Schema(type=openapi.TYPE_STRING),
                                            "email": openapi.Schema(type=openapi.TYPE_STRING),
                                            "profile_pic": openapi.Schema(type=openapi.TYPE_STRING),
                                        }),
                             })
                     })
@api_view(['POST'])
def login(request):
    response = {}
    if request.method == 'POST':
        data = json.loads(request.body)
        if data.get('email', None) and data.get('password', None):
            user = models.User.objects.filter(email=data.get('email')).first()
            if user:
                valid = check_password(data.get('password'), user.password)
                if not valid:
                    response['statusCode'] = const.INVALID_INPUT_ERROR_CODE
                    response['message'] = 'Login Failed! Please enter a correct email and password!'
                else:
                    response['data'] = {}
                    response['data']['user'] = serializers.UserSerializer(user, many=False).data
                    refresh = RefreshToken.for_user(user)
                    response['data']['access'] = str(refresh.access_token)
                    response['data']['refresh'] = str(refresh)
                    response['statusCode'] = const.SUCCESS_STATUS_CODE
                    response['message'] = 'Logged in successfully!'
            else:
                response['statusCode'] = const.USER_NOT_REGISTERED_CODE
                response['message'] = "You're not registered. Please signup!"
        else:
            response['statusCode'] = const.PARAMETER_MISSING_CODE
            response['message'] = const.PARAMETER_MISSING_OR_INVALID_MESSAGE
    else:
        response['statusCode'] = const.METHOD_NOT_ALLOWED_CODE
        response['message'] = 'Method not allowed!'          
    
    return JsonResponse(response)



@swagger_auto_schema(method='post',
                     operation_id='forgot_password',
                     operation_description="Forgot Password",
                     request_body=openapi.Schema(
                                    type=openapi.TYPE_OBJECT,
                                    properties={
                                        'email': openapi.Schema(type=openapi.TYPE_STRING),
                                    }),
                     responses={
                         const.SUCCESS_STATUS_CODE: utils.swagger_data_response(
                             'Password reset instructions sent to your email!',
                             {
                                 
                             })
                     })
@api_view(['POST'])
def forgot_password(request):
    response = {}
    data = json.loads(request.body)
    if data.get('email', None):
        user = models.User.objects.filter(email=data.get('email')).first()
        if user:
            context = {}
            token = default_token_generator.make_token(user)
            context['link'] = '{}/passwordreset/?token={}&email={}'.format(
                config('FRONTEND_URL'),
                token,
                user.email
            )
            # Send email here
            
            
            response['data'] = {}
            response['statusCode'] = const.SUCCESS_STATUS_CODE
            response['message'] = 'Password reset instructions sent to your email!'
        else:
            response['statusCode'] = const.USER_NOT_REGISTERED_CODE
            response['message'] = const.USER_NOT_REGISTERED_MESSAGE
    else:
        response['statusCode'] = const.PARAMETER_MISSING_CODE
        response['message'] = const.PARAMETER_MISSING_MESSAGE
    
    return JsonResponse(response)


@swagger_auto_schema(method='post',
                     operation_id='reset_password',
                     operation_description="Reset Password",
                     request_body=openapi.Schema(
                                    type=openapi.TYPE_OBJECT,
                                    properties={
                                        'email': openapi.Schema(type=openapi.TYPE_STRING),
                                        'token': openapi.Schema(type=openapi.TYPE_STRING),
                                        'password': openapi.Schema(type=openapi.TYPE_STRING),
                                        'confirm_password': openapi.Schema(type=openapi.TYPE_STRING),
                                    }),
                     responses={
                         const.SUCCESS_STATUS_CODE: utils.swagger_data_response(
                             'Password updated successfully!',
                             {

                             })
                     })
@api_view(['POST'])
def reset_password(request):
    response = {}
    if request.method == 'POST':
        data = json.loads(request.body)
        if data.get('token', None) and data.get('email', None) and data.get('password', None) and data.get('confirm_password', None):
            if data.get('password') == data.get('confirm_password'):
                user = models.User.objects.filter(email=data.get('email')).first()
                if user:
                    previous_password = check_password(data.get('password'), user.password)
                    if not previous_password:
                        valid_token = default_token_generator.check_token(user, data.get('token'))
                        if valid_token:
                            user.password = make_password(data.get('password'))
                            user.save()
                            response['statusCode'] = const.SUCCESS_STATUS_CODE
                            response['message'] = 'Password updated successfully!'
                        else:
                            response['statusCode'] = const.INVALID_INPUT_ERROR_CODE
                            response['message'] = 'Token Expired or Wrong!'
                    else:
                        response['statusCode'] = const.INVALID_INPUT_ERROR_CODE
                        response['message'] = 'Please do not use old password!'
                else:
                    response['statusCode'] = const.USER_NOT_REGISTERED_CODE
                    response['message'] = const.USER_NOT_REGISTERED_MESSAGE
            else:
                response['statusCode'] = const.PARAMETER_VALIDATION
                response['message'] = 'Passwords not matching!'
        else:
            response['statusCode'] = const.PARAMETER_MISSING_CODE
            response['message'] = const.PARAMETER_MISSING_MESSAGE
    else:
        response['statusCode'] = const.METHOD_NOT_ALLOWED_CODE
        response['message'] = const.METHOD_NOT_ALLOWED_MESSAGE
    
    return JsonResponse(response)

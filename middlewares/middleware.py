import jwt
import json

from django.utils.functional import SimpleLazyObject
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import AnonymousUser
from django.db.models import Q
from django.conf import LazySettings
from django.http import HttpResponse, JsonResponse

from app import models
from project_name import constants

settings = LazySettings()


class DisableCSRF(MiddlewareMixin):

    def process_request(self, request):
        setattr(request, '_dont_enforce_csrf_checks', True)


class JWTAuthenticationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if not request.path.startswith(constants.AVOID_AUTHENTICATION):
            token = request.META.get('HTTP_AUTHORIZATION', None)
            if not token:
                response = {}
                response['data'] = {}
                response['message'] = constants.ACCESS_TOKEN_MISSING_MESSAGE
                response['statusCode'] = constants.ACCESS_TOKEN_ERROR_CODE
                return HttpResponse(json.dumps(response), content_type="application/json")
            else:
                try:
                    user = SimpleLazyObject(lambda: self.__class__.get_jwt_user(request))
                    if user and user.is_active:
                        request.user = user
                    else:
                        response = {}
                        response['data'] = {}
                        response['message'] = constants.ACCESS_TOKEN_WRONG_MESSAGE
                        response['statusCode'] = constants.ACCESS_TOKEN_ERROR_CODE
                        return HttpResponse(json.dumps(response), content_type="application/json")

                except Exception as e:
                    response = {}
                    response['data'] = {}
                    response['message'] = constants.ACCESS_TOKEN_WRONG_MESSAGE
                    response['statusCode'] = constants.ACCESS_TOKEN_ERROR_CODE
                    return HttpResponse(json.dumps(response), content_type="application/json")

    @staticmethod
    def get_jwt_user(request):
        token = request.META.get('HTTP_AUTHORIZATION', None)
        user_jwt = None
        # user_jwt = AnonymousUser()
        if token is not None:
            try:
                user_jwt = jwt.decode(
                    token,
                    settings.SECRET_KEY,
                )
                user_jwt = models.User.objects.get(
                    id=user_jwt['user_id']
                )
            except Exception as e:
                return None
        else:
            return None
        return user_jwt


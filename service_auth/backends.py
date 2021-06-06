import jwt
from jwt.exceptions import DecodeError

from django.conf import settings

from rest_framework import authentication, exceptions

from .models import CustomUser as User


def authenticate_credentials(request, token):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY)
    except DecodeError:
        msg = 'Invalid authentication. Could not decode token.'
        raise exceptions.AuthenticationFailed(msg)

    try:
        user = User.objects.get(pk=payload['id'])
    except User.DoesNotExist:
        msg = 'No user matching this token was found.'
        raise exceptions.AuthenticationFailed(msg)

    return user, token


class JWTAuthentication(authentication.BaseAuthentication):
    authentication_header_prefix = 'Bearer'

    def authenticate(self, request):
        request.user = None
        auth_header = authentication.get_authorization_header(request).split()
        auth_header_prefix = self.authentication_header_prefix.lower()
        if not auth_header:
            return None
        if len(auth_header) == 1:
            return None
        elif len(auth_header) > 2:
            return None
        prefix = auth_header[0].decode('utf-8')
        token = auth_header[1].decode('utf-8')

        if prefix.lower() != auth_header_prefix:
            return None
        return authenticate_credentials(request, token)

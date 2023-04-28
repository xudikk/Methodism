#  Created by Xudoyberdi Egamberdiyev
#
#  Please contact before making any changes
#
#  Tashkent, Uzbekistan


from django.contrib.auth import get_user_model, authenticate
from rest_framework.authentication import TokenAuthentication, get_authorization_header, BasicAuthentication
from rest_framework.generics import GenericAPIView
from rest_framework import exceptions

from methodism.helper import custom_response
from methodism.error_messages import MESSAGE
import base64, binascii


# Custom Holatdagi bazi classlar sizga ishlashganda optimallik uchun xizmat qiladi
class CustomBasicAuthentication(BasicAuthentication):
    def authenticate(self, request):
        auth = get_authorization_header(request).split()

        if not auth or auth[0].lower() != b'basic':
            return None

        if len(auth) == 1:
            msg = custom_response(False, message=MESSAGE['InvalidBasicHeader1'])
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = custom_response(False, message=MESSAGE['InvalidBasicHeader2'])
            raise exceptions.AuthenticationFailed(msg)

        try:
            try:
                auth_decoded = base64.b64decode(auth[1]).decode('utf-8')
            except UnicodeDecodeError:
                auth_decoded = base64.b64decode(auth[1]).decode('latin-1')
            auth_parts = auth_decoded.partition(':')
        except (TypeError, UnicodeDecodeError, binascii.Error):
            msg = custom_response(False, message=MESSAGE['InvalidBasicHeader3'])
            raise exceptions.AuthenticationFailed(msg)

        userid, password = auth_parts[0], auth_parts[2]
        return self.authenticate_credentials(userid, password, request)

    def authenticate_credentials(self, userid, password, request=None):
        credentials = {
            get_user_model().USERNAME_FIELD: userid,
            'password': password
        }
        user = authenticate(request=request, **credentials)

        if user is None:
            raise exceptions.AuthenticationFailed(custom_response(False, message=MESSAGE['UserPasswordError']))

        if not user.is_active:
            raise exceptions.AuthenticationFailed(custom_response(False, message=MESSAGE['UserDeleted']))

        return (user, None)

    def authenticate_header(self, request):
        return 'Basic realm="%s"' % self.www_authenticate_realm


class CustomGenericAPIView(GenericAPIView):
    def permission_denied(self, request, message=None, code=None):
        if request.authenticators and not request.successful_authenticator:
            raise exceptions.NotAuthenticated(custom_response(False, message=MESSAGE['NotAuthenticated']))
        raise exceptions.PermissionDenied(detail=MESSAGE['PermissionDenied'], code=code)


class BearerAuth(TokenAuthentication):
    keyword = 'Bearer'

    def authenticate_credentials(self, key):
        model = self.get_model()
        try:
            token = model.objects.select_related('user').get(key=key)
        except model.DoesNotExist:
            raise exceptions.AuthenticationFailed(custom_response(False, message=MESSAGE['Unauthenticated']))

        if not token.user.is_active:
            raise exceptions.AuthenticationFailed(custom_response(False, message=MESSAGE['UserNot']))

        if token.user.deleted:
            raise exceptions.AuthenticationFailed(custom_response(False, message=MESSAGE['UserDeleted']))

        return super(BearerAuth, self).authenticate_credentials(key)

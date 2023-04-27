#  Created by Xudoyberdi Egamberdiyev
#
#  Please contact before making any changes
#
#  Tashkent, Uzbekistan

from rest_framework.authtoken.models import Token
from base.costumizing import CustomGenericAPIView
from base.decors import method_and_params_checker
from rest_framework.response import Response
from re import compile as re_compile

from base.error_messages import MESSAGE
from base.helper import custom_response, exception_data


class METHODIZM(CustomGenericAPIView):
    """
                        Main Class | METHODIZM
    file -> Asosiy funksiyalar joylashgan fileni ko'rsating
    token_key -> Token Secret kalitini ko'rsating (default=Bearer)
    auth_headers -> API headersda ushlab olinishi kerak bo'lgan kalitni ko'rsating (default=Authorization)
    token_class -> Ro'yxatdan o'tganligini ko'rsatuvchi classni ko'rsating -> (default=Token)
    not_auth_methods -> Ro'yxatdan o'tish talab qilinmaydigan funksiyalarni ko'rsating | list ko'rinishida
    response_funk -> Imkon qadar teginilmagan ma'qul!

    Bunga qo'shimcha boshqa Custom holardagi avtorizatsiyalardan ham foydalanishingiz mumkin

    EXP:
        authentication_classes = CustomBasicAuthentication,
        permission_classes = IsAuthenticated,

    DIQQAT !!!  BearerAuth yoki TokenAuthentication classlaridan foydalanish mumkin emas!!!
    """

    file = "__main__"
    token_key = "Bearer"
    auth_headers = 'Authorization'
    token_class = Token
    not_auth_methods = []  # def hello_world() => hello.world
    response_funk = custom_response  # must be funk(status, data, method ,message) return dict {}

    @method_and_params_checker
    def post(self, requests, *args, **kwargs):
        method = requests.data.get("method")
        params = requests.data.get("params")
        headers = requests.headers
        if not self.authentication_classes and not self.permission_classes and method not in self.not_auth_methods:
            authorization = headers.get(self.auth_headers, '')
            pattern = re_compile(self.token_key + r" (.+)")

            if not pattern.match(authorization):
                return Response(self.response_funk(status=False, method=method, message=MESSAGE['NotAuthenticated']))
            input_token = pattern.findall(authorization)[0]

            # Authorize
            token = self.token_class.objects.filter(key=input_token).first()
            if not token:
                return Response(self.response_funk(status=False, method=method, message=MESSAGE['AuthToken']))
            requests.user = token.user
        try:
            funk = getattr(self.file, method.replace('.', '_').replace('-', '_'))
        except AttributeError:
            return Response(self.response_funk(False, method=method, message=MESSAGE['MethodDoesNotExist']))
        except Exception as e:
            return Response(self.response_funk(False, method=method, message=MESSAGE['UndefinedError'],
                                               data=exception_data(e)))
        res = map(funk, [requests], [params])
        try:
            response = Response(list(res)[0])
            response.data.update({'method': method})
        except Exception as e:
            response = Response(self.response_funk(False, method=method, message=MESSAGE['UndefinedError'],
                                                   data=exception_data(e)))
        return response

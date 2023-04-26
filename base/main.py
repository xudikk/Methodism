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

    """
    file = "__main__"
    token_key = "Bearer"
    auth_headers = 'Authorization'
    token_class = Token
    not_auth_methods = []  # def hello_world() => hello.world

    @method_and_params_checker
    def post(self, requests, *args, **kwargs):
        method = requests.data.get("method")
        params = requests.data.get("params")
        headers = requests.headers
        if method not in self.not_auth_methods:
            authorization = headers.get(self.auth_headers, '')
            pattern = re_compile(self.token_key + r" (.+)")

            if not pattern.match(authorization):
                return Response(custom_response(status=False, method=method, message=MESSAGE['NotAuthenticated']))
            input_token = pattern.findall(authorization)[0]

            # Authorize
            token = self.token_class.objects.filter(key=input_token).first()
            if not token:
                return Response(custom_response(status=False, method=method, message=MESSAGE['AuthToken']))
            requests.user = token.user
        try:
            funk = getattr(self.file, method.replace('.', '_').replace('-', '_'))
        except AttributeError:
            return Response(custom_response(False, method=method, message=MESSAGE['MethodDoesNotExist']))
        except Exception as e:
            return Response(custom_response(False, method=method, message=MESSAGE['UndefinedError'],
                                            data=exception_data(e)))
        res = map(funk, [requests], [params])
        try:
            response = Response(list(res)[0])
            response.data.update({'method': method})
        except Exception as e:
            response = Response(custom_response(False, method=method, message=MESSAGE['UndefinedError'],
                                                data=exception_data(e)))
        return response


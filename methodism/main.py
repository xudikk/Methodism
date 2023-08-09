#  Created by Xudoyberdi Egamberdiyev
#
#  Please contact before making any changes
#
#  Tashkent, Uzbekistan
from contextlib import closing

from django.db import connection
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

from re import compile as re_compile

from methodism.costumizing import CustomGenericAPIView
from methodism.decors import method_and_params_checker
from methodism.error_messages import MESSAGE
from methodism.helper import custom_response, exception_data, dictfetchone, dictfetchall


class METHODISM(CustomGenericAPIView):
    """
                        Main Class | METHODIZM
    file -> Asosiy funksiyalar joylashgan fileni ko'rsating, E.X: from qayer import file_nom, file=file_nom
    token_key -> Token Secret kalitini ko'rsating (default=Bearer)
    auth_headers -> API headersda ushlab olinishi kerak bo'lgan kalitni ko'rsating (default=Authorization)
    token_class -> Ro'yxatdan o'tganligini ko'rsatuvchi classni ko'rsating -> (default=Token)
    not_auth_methods -> Ro'yxatdan o'tish talab qilinmaydigan funksiyalarni ko'rsating | list ko'rinishida

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

    @method_and_params_checker
    def post(self, requests, *args, **kwargs):
        method = requests.data.get("method")
        params = requests.data.get("params")
        headers = requests.headers
        if method not in self.not_auth_methods and "*" not in self.not_auth_methods:
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


class SqlAPIMethodism(CustomGenericAPIView):
    """
                            Main Class | METHODIZM
        file -> Asosiy funksiyalar joylashgan fileni ko'rsating, E.X: from qayer import file_nom, file=file_nom
        token_key -> Token Secret kalitini ko'rsating (default=Bearer)
        auth_headers -> API headersda ushlab olinishi kerak bo'lgan kalitni ko'rsating (default=Authorization)
        token_class -> Ro'yxatdan o'tganligini ko'rsatuvchi classni ko'rsating -> (default=Token)
        not_auth_methods -> Ro'yxatdan o'tish talab qilinmaydigan funksiyalarni ko'rsating | list ko'rinishida

        Methodism sql zaproslarni spiga aylantirib beruvchi class!

        EXP:
            def your_funk(request, params):
                # return "sql zapros"
                return "select colums from your_table", True  # True-returns one, False-returns many


        in methodism your_funk == your.funk

        DIQQAT !!!  BearerAuth yoki TokenAuthentication classlaridan foydalanish mumkin emas!!!


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
        if method not in self.not_auth_methods and "*" not in self.not_auth_methods:
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
        funk = map(funk, [requests], [params])

        # sql code larini ishlatish uchun!
        try:
            sql = list(funk)[0]
            if sql is not tuple:
                return Response(sql)
            with closing(connection.cursor()) as cursor:
                try:
                    cursor.execute(sql[0])
                    result = dictfetchone(cursor) if sql[1] else dictfetchall(cursor)
                    response = Response(custom_response(True, data=result))
                except Exception as e:
                    response = Response(custom_response(False, method=method, message=MESSAGE['UndefinedError'],
                                                        data=exception_data(e)))
            response.data.update({'method': method})

        except Exception as e:
            response = Response(custom_response(False, method=method, message=MESSAGE['UndefinedError'],
                                                data=exception_data(e)))
        return response

#  Created by Xudoyberdi Egamberdiyev
#
#  Please contact before making any changes
#
#  Tashkent, Uzbekistan
import inspect
import logging
from datetime import datetime, timedelta
from importlib import import_module

from django.conf import settings
from django.db import connections, DEFAULT_DB_ALIAS
from django.utils import timezone
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

from methodism.costumizing import CustomGenericAPIView
from methodism.decors import method_and_params_checker, method_checker
from methodism.error_messages import MESSAGE
from methodism.helper import custom_response, exception_data, dictfetchone, dictfetchall

logger = logging.getLogger('methodism')


def normalize_method(method):
    """ "salom.dunyo", "salom-dunyo" va "salom_dunyo" -> "salom_dunyo" """
    return str(method).strip().replace('.', '_').replace('-', '_')


class BaseMethodism(CustomGenericAPIView):
    """
    METHODISM va SqlAPIMethodism uchun umumiy asos class.
    Avtorizatsiya, methodni topish, xatoliklarni ushlash va javob qaytarish shu yerda.

    file -> Asosiy (post zaprosi uchun) funksiyalar joylashgan file (module yoki "app.services" ko'rinishidagi yo'l)
    get_methods -> Asosiy (get zaprosi uchun) funksiyalar joylashgan file (module yoki yo'l)
    token_key -> Token Secret kalitini ko'rsating (default=Bearer)
    auth_headers -> API headersda ushlab olinishi kerak bo'lgan kalitni ko'rsating (default=Authorization)
    token_class -> Ro'yxatdan o'tganligini ko'rsatuvchi classni ko'rsating -> (default=Token)
    not_auth_methods -> Ro'yxatdan o'tish talab qilinmaydigan funksiyalarni ko'rsating | list ko'rinishida
                        ("*" - barcha funksiyalar ochiq)

    Qo'shimcha sozlamalar:
    token_lifetime -> Token amal qilish muddati (timedelta yoki sekundlarda int). None - cheksiz
    use_http_status -> True bo'lsa javobning HTTP statusi "status_code" ga teng bo'ladi (default=False, doim 200)
    show_exception_details -> Xatolik tafsilotlarini javobda ko'rsatish. None - settings.DEBUG ga qarab
    strict_methods -> True bo'lsa faqat file ning o'zida yozilgan funksiyalar chaqiriladi
                      (boshqa joydan import qilinganlari API orqali chaqirilmaydi)
    """

    file = "__main__"
    get_methods = "__main__"  # faqat get methodlari uchun
    token_key = "Bearer"
    auth_headers = 'Authorization'
    token_class = Token
    not_auth_methods = []  # def hello_world() => hello.world

    token_lifetime = None
    use_http_status = False
    show_exception_details = None
    strict_methods = False

    # ********************************* method topish *********************************

    @staticmethod
    def get_source(source):
        if isinstance(source, str):
            try:
                return import_module(source)
            except ImportError:
                logger.warning("Methodism: '%s' moduli topilmadi", source)
                return None
        return source

    def resolve_method(self, source, method):
        name = normalize_method(method)
        # "_" bilan boshlanuvchi (yashirin, __dunder__) nomlarni API orqali chaqirib bo'lmaydi
        if not name.isidentifier() or name.startswith('_'):
            return None

        module = self.get_source(source)
        funk = getattr(module, name, None)
        if funk is None or not callable(funk) or inspect.isclass(funk):
            return None
        if self.strict_methods and inspect.ismodule(module) and getattr(funk, '__module__', None) != module.__name__:
            return None
        return funk

    def is_public(self, method, funk=None):
        if getattr(funk, 'methodism_public', False):
            return True
        allowed = {normalize_method(m) for m in self.not_auth_methods}
        return '*' in allowed or normalize_method(method) in allowed

    # ********************************* avtorizatsiya *********************************

    def get_token_key(self, request):
        authorization = request.headers.get(self.auth_headers, '').strip()
        if not self.token_key:
            return authorization or None
        parts = authorization.split()
        if len(parts) != 2 or parts[0].lower() != self.token_key.lower():
            return None
        return parts[1]

    def get_lifetime(self):
        if self.token_lifetime is None:
            return None
        if isinstance(self.token_lifetime, timedelta):
            return self.token_lifetime
        return timedelta(seconds=int(self.token_lifetime))

    def is_token_expired(self, token):
        lifetime = self.get_lifetime()
        created = getattr(token, 'created', None)
        if lifetime is None or created is None:
            return False
        now = timezone.now() if timezone.is_aware(created) else datetime.now()
        return created + lifetime < now

    def authenticate_request(self, request, method):
        """ Muvaffaqiyatli bo'lsa None, aks holda xatolik javobini (dict) qaytaradi """
        key = self.get_token_key(request)
        if not key:
            return custom_response(False, method=method, message=MESSAGE['NotAuthenticated'], status_code=401)

        token = self.token_class.objects.select_related('user').filter(key=key).first()
        if not token:
            return custom_response(False, method=method, message=MESSAGE['AuthToken'], status_code=401)
        if self.is_token_expired(token):
            return custom_response(False, method=method, message=MESSAGE['TokenExpired'], status_code=401)

        user = token.user
        if not getattr(user, 'is_active', True):
            return custom_response(False, method=method, message=MESSAGE['UserNotActive'], status_code=403)

        request.user = user
        request.auth = token
        return None

    # ********************************* javob *********************************

    def make_response(self, data):
        status = 200
        if self.use_http_status and isinstance(data, dict):
            code = data.get('status_code')
            if isinstance(code, int) and 100 <= code < 600:
                status = code
        return Response(data, status=status)

    def error_response(self, method, e):
        logger.exception("Methodism: '%s' methodida xatolik", method)
        show = self.show_exception_details
        if show is None:
            show = settings.DEBUG
        return custom_response(False, method=method, message=MESSAGE['UndefinedError'],
                               data=exception_data(e) if show else None, status_code=500)

    def process_result(self, result, method):
        """ Funksiya qaytargan natijani javobga aylantiradi (vorislarda o'zgartiriladi) """
        if isinstance(result, dict):
            result['method'] = method
        return result

    # ********************************* asosiy jarayon *********************************

    def run_method(self, request, source, method, params=None, with_params=False):
        funk = self.resolve_method(source, method)

        # avval avtorizatsiya: ro'yxatdan o'tmagan foydalanuvchi qaysi methodlar borligini bila olmasligi uchun
        if not self.is_public(method, funk):
            error = self.authenticate_request(request, method)
            if error is not None:
                return self.make_response(error)

        if funk is None:
            return self.make_response(custom_response(False, method=method, message=MESSAGE['MethodDoesNotExist'],
                                                      status_code=404))
        try:
            result = funk(request, params) if with_params else funk(request)
            data = self.process_result(result, method)
        except Exception as e:
            data = self.error_response(method, e)
        return self.make_response(data)

    @method_and_params_checker
    def post(self, request, *args, **kwargs):
        return self.run_method(request, self.file, request.data.get("method"), request.data.get("params"),
                               with_params=True)

    @method_checker
    def get(self, request, *args, **kwargs):
        return self.run_method(request, self.get_methods, request.GET.get("method"))


class METHODISM(BaseMethodism):
    """
                        Main Class | METHODIZM
    file -> Asosiy funksiyalar joylashgan fileni ko'rsating, E.X: from qayer import file_nom, file=file_nom
            yoki yo'l ko'rinishida: file = "app.services"
    get_methods -> Asosiy (get zaprosi uchun) funksiyalar joylashgan fileni ko'rsating, E.X: from qayer import file_nom, get_methods=file_nom
    token_key -> Token Secret kalitini ko'rsating (default=Bearer)
    auth_headers -> API headersda ushlab olinishi kerak bo'lgan kalitni ko'rsating (default=Authorization)
    token_class -> Ro'yxatdan o'tganligini ko'rsatuvchi classni ko'rsating -> (default=Token)
    not_auth_methods -> Ro'yxatdan o'tish talab qilinmaydigan funksiyalarni ko'rsating | list ko'rinishida
    token_lifetime, use_http_status, show_exception_details, strict_methods -> BaseMethodism ga qarang


    ***************************************** Post method *****************************************************

    EXP:
        def your_funk(request, params):
            # your codes
            return result   # result -> dict da bo'lishi kerak (methodism.helper.custom_reponse() funksiyasidan foydalanish mumkin)
    # so'rov yuborilganda:
        your_domen/your_api_url/
        body(Json):
            {
                method: "your.funk",
                params: {}
            }


    ****************************************** get method  *******************************************************

    EXP:
        def your_funk(request):
            # your codes
            return result   # result -> dict da bo'lishi kerak (methodism.helper.custom_reponse() funksiyasidan foydalanish mumkin)

        # so'rov yuborilganda:
            your_domen/your_api_url/?method=your.funk

    in methodism your_funk == your.funk == your-funk



    Bunga qo'shimcha boshqa Custom holardagi avtorizatsiyalardan ham foydalanishingiz mumkin

    EXP:
        authentication_classes = CustomBasicAuthentication,
        permission_classes = IsAuthenticated,



    DIQQAT !!!  BearerAuth yoki TokenAuthentication classlaridan foydalanish mumkin emas!!!
    """


class SqlAPIMethodism(BaseMethodism):
    """
                            Main Class | METHODIZM
        file -> Asosiy (post zaprosi uchun) funksiyalar joylashgan fileni ko'rsating, E.X: from qayer import file_nom, file=file_nom
        get_methods -> Asosiy (get zaprosi uchun) funksiyalar joylashgan fileni ko'rsating, E.X: from qayer import file_nom, get_methods=file_nom
        token_key -> Token Secret kalitini ko'rsating (default=Bearer)
        auth_headers -> API headersda ushlab olinishi kerak bo'lgan kalitni ko'rsating (default=Authorization)
        token_class -> Ro'yxatdan o'tganligini ko'rsatuvchi classni ko'rsating -> (default=Token)
        not_auth_methods -> Ro'yxatdan o'tish talab qilinmaydigan funksiyalarni ko'rsating | list ko'rinishida
        database -> qaysi bazada ishlatilishi (settings.DATABASES dagi kalit, default="default")

        Methodism sql zaproslarni apiga aylantirib beruvchi class!

        EXP(post func):
            def your_funk(request, params):
                # return "sql zapros"
                return "select colums from your_table", True  # True-returns one, False-returns many

            # XAVFSIZ USUL (SQL injectiondan himoyalangan) - parametrlar 3-qiymat sifatida beriladi:
            def your_funk(request, params):
                return "select * from your_table where id = %s", True, [params['id']]

        EXP(get func):
        def your_funk(request):
                # return "sql zapros"
                return "select colums from your_table", True  # True-returns one, False-returns many


        in methodism your_funk == your.funk

        DIQQAT !!!  BearerAuth yoki TokenAuthentication classlaridan foydalanish mumkin emas!!!
        DIQQAT !!!  params ni hech qachon f-string orqali sql ga qo'shmang, 3-qiymat sifatida bering!

    """

    database = DEFAULT_DB_ALIAS

    def execute_sql(self, sql, one=False, sql_params=None):
        with connections[self.database].cursor() as cursor:
            cursor.execute(sql, sql_params)
            return dictfetchone(cursor) if one else dictfetchall(cursor)

    def process_result(self, result, method):
        if isinstance(result, tuple) and len(result) in (2, 3):
            data = self.execute_sql(*result)
            return custom_response(True, data=data, method=method)

        if isinstance(result, dict):
            # funksiya tayyor custom_response qaytargan bo'lsa o'zgartirmasdan qaytariladi
            if 'status' in result and 'data' in result:
                result['method'] = method
                return result
            # README dagi {"error": "..."} ko'rinishidagi xatoliklar
            if 'error' in result:
                return custom_response(False, data=result, method=method, status_code=400)
        return custom_response(True, data=result, method=method)

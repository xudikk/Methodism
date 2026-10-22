#  Created by Xudoyberdi Egamberdiyev
#
#  Please contact before making any changes
#
#  Tashkent, Uzbekistan
from functools import wraps

from rest_framework.response import Response

from methodism.error_messages import MESSAGE, error_params_unfilled
from methodism.helper import custom_response


def _respond(view, data):
    # view da make_response bo'lsa (METHODISM classlari) o'shandan foydalaniladi
    make_response = getattr(view, 'make_response', None)
    return make_response(data) if make_response else Response(data)


# asosiy decorator method va params kalitlarini tekshirib oluvchi funksiya
def method_and_params_checker(funk):
    @wraps(funk)
    def wrapper(self, req, *args, **kwargs):
        if not isinstance(req.data, dict):
            return _respond(self, custom_response(False, message=MESSAGE['InvalidBody'], status_code=400))

        method = req.data.get("method")
        if not method:
            return _respond(self, custom_response(False, method=method, message=MESSAGE['MethodMust'],
                                                  status_code=400))
        if req.data.get('params') is None:
            return _respond(self, custom_response(False, method=method, message=MESSAGE['ParamsMust'],
                                                  status_code=400))
        return funk(self, req, *args, **kwargs)

    return wrapper


def method_checker(funk):
    @wraps(funk)
    def wrapper(self, req, *args, **kwargs):
        method = req.GET.get("method", None)
        if not method:
            return _respond(self, custom_response(False, method=method, message=MESSAGE['MethodMust'],
                                                  status_code=400))
        return funk(self, req, *args, **kwargs)

    return wrapper


# ********************** Siz yozadigan funksiyalar uchun decoratorlar **********************

def params_required(*names):
    """
    params ichida kerakli kalitlar borligini tekshiradi.

    EXP:
        @params_required('phone', 'password')
        def login(request, params):
            ...
    """

    def decorator(funk):
        @wraps(funk)
        def wrapper(request, params, *args, **kwargs):
            if not isinstance(params, dict):
                return custom_response(False, message=MESSAGE['ParamsMustDict'], status_code=400)
            missing = [name for name in names if params.get(name) in (None, '')]
            if missing:
                return custom_response(False, message=error_params_unfilled(', '.join(missing)),
                                       data={'missing': missing}, status_code=400)
            return funk(request, params, *args, **kwargs)

        return wrapper

    return decorator


def public_method(funk):
    """
    Funksiyani ro'yxatdan o'tmagan foydalanuvchilar uchun ham ochiq qiladi
    (not_auth_methods ga yozish o'rniga ishlatish mumkin).

    EXP:
        @public_method
        def auth_login(request, params):
            ...
    """
    funk.methodism_public = True
    return funk

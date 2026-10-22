#  Created by Xudoyberdi Egamberdiyev
#
#  Please contact before making any changes
#
#  Tashkent, Uzbekistan
import binascii
import os
import base64
import traceback
from django.conf import settings
from collections import namedtuple

LANGUAGES = ('uz', 'ru', 'en')
DEFAULT_LANG = 'en'


# natijalarni custom Holatda chiqaradi
def custom_response(status, data=None, message=None, method=None, status_code=200):
    if type(status) is not bool:
        status = False
    return {
        "Origin": getattr(settings, 'APP_NAME', 'Methodism'),
        "method": method,
        "status": status,
        "status_code": status_code,
        "data": data,
        "message": message
    }


# xatolikni ushash uchun funksiya
def exception_data(e):
    exc_type = type(e)
    name = exc_type.__qualname__
    if exc_type.__module__ not in ('builtins', '__main__'):
        name = f"{exc_type.__module__}.{name}"

    # xatolik aynan qaysi qatorda yuz berganini ko'rsatish uchun eng ichki frame olinadi
    frames = traceback.extract_tb(e.__traceback__) if e.__traceback__ else []
    last = frames[-1] if frames else None
    return {
        "value": f"{name} => {e}",
        "line": str(last.lineno) if last else None,
        "frame": f"{last.filename}:{last.lineno} in {last.name}" if last else None,
    }


# berilgan uzunlikdagi Random token generatsiya qilib beradi
def generate_key(size=50):
    return binascii.hexlify(os.urandom(size)).decode()


# b64 orqali l marta shifrlaydi va shifrdan ochadi
def code_decoder(code, decode=False, l=1):
    if decode:
        for i in range(l):
            code = base64.b64decode(code).decode()
        return code
    else:
        for i in range(l):
            code = base64.b64encode(str(code).encode()).decode()
        return code


# for SQL Methodism
def namedtuplefetchall(cursor):
    "cursordan kelayotgan tablitsa ichidagi barcha qatorlarni namedtuple ko'rinishida qaytaradi"
    desc = cursor.description
    nt_result = namedtuple('Result', [col[0] for col in desc])
    return [nt_result(*row) for row in cursor.fetchall()]


def dictfetchall(cursor):
    "cursordan kelayotgan tablitsa ichidagi barcha qatorlarni dict ko'rinishida qaytaradi"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


def dictfetchone(cursor):
    "cursordan kelayotgan tablitsa ichidagi bitta qatorni dict ko'rinishida qaytaradi"
    row = cursor.fetchone()
    if row is None:
        return False
    columns = [col[0] for col in cursor.description]
    return dict(zip(columns, row))


def auto_dict(data=None, model=True, exclude=('id', 'user', 'password'), **kwargs):
    """
    Kirib kelgan model objectini avtomatik tarzda dictga o'girib beradi.
    exclude -> chiqarilmasligi kerak bo'lgan maydonlar (password hech qachon chiqarilmaydi)
    kwargs  -> natijaga qo'shimcha qo'shiladigan kalitlar
    """
    result = {}
    if model and data is not None:
        exclude = set(exclude) | {'password'}
        for field in data._meta.concrete_fields:
            if field.name in exclude or field.attname in exclude:
                continue
            result[field.attname] = getattr(data, field.attname)
    result.update(kwargs)
    return result


# eski nom bilan ham ishlashi uchun
_auto_dict = auto_dict


def lang_helper(request, default=DEFAULT_LANG):
    """
    So'rov uchun tilni aniqlaydi:
        1. user.lang (agar userda shunday maydon bo'lsa)
        2. Accept-Language header
        3. default ('en')
    :param request: WSGI objects
    :return: str
    """
    user = getattr(request, 'user', None)
    lang = getattr(user, 'lang', None) if user is not None and not user.is_anonymous else None
    if lang in LANGUAGES:
        return lang

    header = request.headers.get('Accept-Language', '') if hasattr(request, 'headers') else ''
    for part in header.split(','):
        code = part.split(';')[0].strip()[:2].lower()
        if code in LANGUAGES:
            return code
    return default


def translate(message, lang=DEFAULT_LANG):
    """
    MESSAGE lug'atidagi {'uz': .., 'ru': .., 'en': ..} ko'rinishidagi xabardan kerakli tildagisini qaytaradi.
    EXP: translate(MESSAGE['NotData'], lang_helper(request))
    """
    if isinstance(message, dict):
        return message.get(lang) or message.get(DEFAULT_LANG) or next(iter(message.values()), None)
    return message

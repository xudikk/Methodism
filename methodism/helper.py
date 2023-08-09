#  Created by Xudoyberdi Egamberdiyev
#
#  Please contact before making any changes
#
#  Tashkent, Uzbekistan
import binascii
import os
import base64
from django.conf import settings
from collections import namedtuple


# natijalarni custom Holatda chiqaradi
def custom_response(status, data=None, message=None, method=None):
    if type(status) is not bool:
        status = False
    return {
        "Origin": settings.APP_NAME,
        "method": method,
        "status": status,
        "data": data,
        "message": message
    }


# xatolikni ushash uchun funksiya
def exception_data(e):
    return {
        "value": f"""{str(type(e)).strip("<class '").strip("'>")} => {str(e.__str__())}""",
        "line": str(e.__traceback__.tb_lineno),
        "frame": str(e.__traceback__.tb_frame),
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


def _auto_dict(data=None, model=True, **kwargs):
    lst = []
    if model:
        for i in data.__dir__():
            if i == "_state" or i == "id" or i == 'user':
                continue
            elif i == "__module__" or i == "_password":
                break
            lst.append(
                (f"{i}", data.__getattribute__(i))
            )
    lst.extend(kwargs.items())
    return dict(lst)

import os  # noqa: F401  - modul API orqali chaqirilmasligi kerak
from django.contrib.auth import get_user_model  # noqa: F401  - strict_methods tekshiruvi uchun

from methodism import custom_response, params_required, public_method


def hello_world(request, params):
    return custom_response(True, data={"hello": "world", "user": request.user.username})


def echo(request, params):
    return custom_response(True, data=params)


def boom(request, params):
    return 1 / 0


@public_method
@params_required("phone", "password")
def auth_login(request, params):
    return custom_response(True, data={"phone": params["phone"]})


def _secret(request, params):
    return custom_response(True, data="secret")


def items(request):
    return [1, 2, 3]


def user_by_name(request, params):
    return "select username from auth_user where username = %s", True, [params["username"]]


def all_users(request, params):
    return "select username from auth_user order by username", False


def sql_error(request, params):
    return {"error": "xatolik"}

from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.test import RequestFactory
from django.utils import timezone
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from methodism import exception_data, translate, lang_helper, auto_dict, MESSAGE
from methodism.sqlpaginator import SqlPaginator
from tests.models import LongToken, PhoneOtp

pytestmark = pytest.mark.django_db


@pytest.fixture
def user():
    return get_user_model().objects.create_user(username="ali", password="secret123")


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def auth_client(user):
    token = Token.objects.create(user=user)
    c = APIClient()
    c.credentials(HTTP_AUTHORIZATION=f"Bearer {token.key}")
    return c


def call(c, url, method, params=None, **extra):
    return c.post(url, {"method": method, "params": {} if params is None else params}, format="json", **extra)


# ---------------------------------------------------------------- body tekshiruvi

def test_method_required(client):
    data = client.post("/api/", {"params": {}}, format="json").json()
    assert data["status"] is False
    assert data["message"] == MESSAGE["MethodMust"]


def test_method_checked_before_params(client):
    # ikkalasi ham yo'q bo'lsa avval method haqida xabar berilishi kerak
    data = client.post("/api/", {}, format="json").json()
    assert data["message"] == MESSAGE["MethodMust"]


def test_params_required(client):
    data = client.post("/api/", {"method": "echo"}, format="json").json()
    assert data["message"] == MESSAGE["ParamsMust"]


def test_body_must_be_object(client):
    data = client.post("/api/", [1, 2], format="json").json()
    assert data["message"] == MESSAGE["InvalidBody"]


# ---------------------------------------------------------------- avtorizatsiya

def test_requires_auth(client):
    data = call(client, "/api/", "hello.world").json()
    assert data["message"] == MESSAGE["NotAuthenticated"]
    assert data["status_code"] == 401


def test_wrong_token(client):
    data = call(client, "/api/", "hello.world", HTTP_AUTHORIZATION="Bearer xyz").json()
    assert data["message"] == MESSAGE["AuthToken"]


def test_authorized_call(auth_client):
    data = call(auth_client, "/api/", "hello.world").json()
    assert data["status"] is True
    assert data["data"] == {"hello": "world", "user": "ali"}
    assert data["method"] == "hello.world"
    assert data["Origin"] == "TestApp"


def test_method_name_variants(auth_client):
    for name in ("hello.world", "hello-world", "hello_world"):
        assert call(auth_client, "/api/", name).json()["status"] is True


def test_not_auth_methods(client):
    data = call(client, "/api/", "echo", {"a": 1}).json()
    assert data["status"] is True and data["data"] == {"a": 1}


def test_public_method_decorator_and_params_required(client):
    data = call(client, "/api/", "auth.login", {"phone": "99890"}).json()
    assert data["status"] is False
    assert data["data"] == {"missing": ["password"]}

    data = call(client, "/api/", "auth.login", {"phone": "99890", "password": "x"}).json()
    assert data["status"] is True


def test_inactive_user(user, auth_client):
    user.is_active = False
    user.save()
    data = call(auth_client, "/api/", "hello.world").json()
    assert data["message"] == MESSAGE["UserNotActive"]


def test_token_lifetime(user):
    token = Token.objects.create(user=user)
    c = APIClient()
    c.credentials(HTTP_AUTHORIZATION=f"Bearer {token.key}")
    assert call(c, "/expiring/", "hello.world").json()["status"] is True

    Token.objects.filter(pk=token.pk).update(created=timezone.now() - timedelta(hours=2))
    assert call(c, "/expiring/", "hello.world").json()["message"] == MESSAGE["TokenExpired"]


def test_custom_token_model(user):
    token = LongToken.objects.create(user=user)
    assert len(token.key) == 200
    c = APIClient()
    c.credentials(HTTP_AUTHORIZATION=f"Bearer {token.key}")
    assert call(c, "/custom/", "hello.world").json()["status"] is True


def test_unknown_method_needs_auth_first(client):
    # ro'yxatdan o'tmagan foydalanuvchi qaysi methodlar borligini bila olmaydi
    assert call(client, "/api/", "nope").json()["message"] == MESSAGE["NotAuthenticated"]


# ---------------------------------------------------------------- method topish xavfsizligi

def test_unknown_method(auth_client):
    data = call(auth_client, "/api/", "nope").json()
    assert data["message"] == MESSAGE["MethodDoesNotExist"]
    assert data["status_code"] == 404


@pytest.mark.parametrize("name", ["_secret", "__dict__", "os", "custom_response.__call__", "a b"])
def test_private_and_non_function_names_blocked(auth_client, name):
    assert call(auth_client, "/api/", name).json()["message"] == MESSAGE["MethodDoesNotExist"]


def test_strict_methods(client):
    assert call(client, "/strict/", "echo", {"x": 1}).json()["status"] is True
    # boshqa moduldan import qilingan funksiya chaqirilmaydi
    assert call(client, "/strict/", "get_user_model").json()["message"] == MESSAGE["MethodDoesNotExist"]


# ---------------------------------------------------------------- xatoliklar

def test_exception_hidden_when_not_debug(auth_client):
    data = call(auth_client, "/api/", "boom").json()
    assert data["status"] is False
    assert data["message"] == MESSAGE["UndefinedError"]
    assert data["data"] is None
    assert data["status_code"] == 500


def test_exception_details_and_http_status(user):
    token = Token.objects.create(user=user)
    c = APIClient()
    c.credentials(HTTP_AUTHORIZATION=f"Bearer {token.key}")
    response = call(c, "/http/", "boom")
    assert response.status_code == 500
    assert response.json()["data"]["value"] == "ZeroDivisionError => division by zero"
    assert "boom" in response.json()["data"]["frame"]


def test_http_status_default_200(client):
    assert call(client, "/api/", "hello.world").status_code == 200


# ---------------------------------------------------------------- GET

def test_get_returns_list(auth_client):
    data = auth_client.get("/api/?method=items").json()
    assert data == [1, 2, 3]


def test_get_requires_method(auth_client):
    assert auth_client.get("/api/").json()["message"] == MESSAGE["MethodMust"]


# ---------------------------------------------------------------- SQL

def test_sql_parametrized(client, user):
    data = call(client, "/sql/", "user.by.name", {"username": "ali"}).json()
    assert data["status"] is True and data["data"] == {"username": "ali"}
    assert data["method"] == "user.by.name"

    # SQL injection ishlamaydi
    data = call(client, "/sql/", "user.by.name", {"username": "' or '1'='1"}).json()
    assert data["data"] is False


def test_sql_many(client, user):
    get_user_model().objects.create_user(username="vali")
    data = call(client, "/sql/", "all.users").json()
    assert data["data"] == [{"username": "ali"}, {"username": "vali"}]


def test_sql_error_dict(client):
    data = call(client, "/sql/", "sql.error").json()
    assert data["status"] is False and data["data"] == {"error": "xatolik"}


def test_sql_passthrough_custom_response(client):
    data = call(client, "/sql/", "echo", {"a": 1}).json()
    assert data["status"] is True and data["data"] == {"a": 1}


# ---------------------------------------------------------------- helperlar

def test_exception_data_module_name():
    class accounts_error(Exception):
        pass

    accounts_error.__module__ = "accounts.errors"
    try:
        raise accounts_error("x")
    except Exception as e:
        assert exception_data(e)["value"] == "accounts.errors.test_exception_data_module_name.<locals>.accounts_error => x"


def test_translate_and_lang_helper():
    assert translate(MESSAGE["NotData"], "ru") == "Информация не найдена"
    assert translate("plain", "ru") == "plain"
    request = RequestFactory().get("/", HTTP_ACCEPT_LANGUAGE="ru-RU,ru;q=0.9")
    assert lang_helper(request) == "ru"
    assert lang_helper(RequestFactory().get("/")) == "en"


def test_auto_dict(user):
    data = auto_dict(user, extra=1)
    assert "password" not in data and "id" not in data
    assert data["username"] == "ali" and data["extra"] == 1


def test_sql_paginator():
    request = RequestFactory().get("/list/?page=2")
    p = SqlPaginator(request, page=2, per_page=10, count=35)
    assert (p.limit, p.offset, p.num_pages()) == (10, 10, 4)
    resp = p.get_paginated_response()
    assert resp["next"].endswith("page=3")
    assert resp["previous"] == "http://testserver/list/"
    assert SqlPaginator(request, page="abc").page_num == 1
    assert SqlPaginator(request, per_page=1000, max_per_page=50).per_page == 50


def test_otp():
    otp = PhoneOtp.objects.create(key="123")
    assert otp.is_valid()
    for _ in range(3):
        otp.add_try()
    assert otp.is_expired and not otp.is_valid()

from datetime import timedelta

from django.urls import path

from methodism import METHODISM, SqlAPIMethodism
from tests import services
from tests.models import LongToken


class Main(METHODISM):
    file = services
    get_methods = "tests.services"
    not_auth_methods = ["echo"]


class Strict(METHODISM):
    file = services
    strict_methods = True
    not_auth_methods = ["*"]


class Http(METHODISM):
    file = services
    use_http_status = True
    show_exception_details = True


class Expiring(METHODISM):
    file = services
    token_lifetime = timedelta(hours=1)


class Custom(METHODISM):
    file = services
    token_class = LongToken


class Sql(SqlAPIMethodism):
    file = services
    not_auth_methods = ["*"]


urlpatterns = [
    path("api/", Main.as_view()),
    path("strict/", Strict.as_view()),
    path("http/", Http.as_view()),
    path("expiring/", Expiring.as_view()),
    path("custom/", Custom.as_view()),
    path("sql/", Sql.as_view()),
]

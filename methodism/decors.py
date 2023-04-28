#  Created by Xudoyberdi Egamberdiyev
#
#  Please contact before making any changes
#
#  Tashkent, Uzbekistan

from rest_framework.response import Response

from methodism.error_messages import MESSAGE
from methodism.helper import custom_response


# asosiy decorator
def method_and_params_checker(funk):
    def wrapper(self, req, *args, **kwargs):
        params = req.data.get('params')
        method = req.data.get("method")

        return Response(custom_response(status=False, message=MESSAGE['MethodMust'])) if not method else Response(
            custom_response(status=False, message=MESSAGE['ParamsMust'])) if params is None else funk(self, req, *args, **kwargs)

    return wrapper

#  Created by Xudoyberdi Egamberdiyev
#
#  Please contact before making any changes
#
#  Tashkent, Uzbekistan

from rest_framework.response import Response

from methodism.error_messages import MESSAGE
from methodism.helper import custom_response


# asosiy decorator method va params kalitlarini tekshirib oluvchi funksiya
def method_and_params_checker(funk):
    def wrapper(self, req, *args, **kwargs):
        params = req.data.get('params')
        method = req.data.get("method")
        response = {
            not method: Response(custom_response(status=False, method=method, message=MESSAGE['MethodMust'])),
            params is None: Response(custom_response(status=False, method=method, message=MESSAGE['ParamsMust']))
        }
        return response.get(True) or funk(self, req, *args, **kwargs)

    return wrapper

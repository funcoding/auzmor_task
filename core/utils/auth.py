import base64
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import NotAuthenticated

from account.models import Account
from core.utils.response_formatter import ResponseFormatterUtil


class CustomAuthentication(BaseAuthentication):

    def authenticate(self, request, **kwargs):
        auth_header_value = request.META.get("HTTP_AUTHORIZATION", "")
        if auth_header_value:
            username, password = base64.b64decode(request.META["HTTP_AUTHORIZATION"].replace("Basic ", '')).decode(
                'utf-8').split(":")
            account = Account.objects.filter(username=username, auth_id=password).first()
            if account is None:
                raise NotAuthenticated()
            # if not auth:
            #     return None
            # if not authmeth.lower() == "bearer":
            #     return None
            # print("ok")
            request.META.update({"user": account})
        else:
            raise NotAuthenticated()

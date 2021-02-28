import base64
import binascii
import os

import casbin
import pytest
from fastapi import FastAPI
from starlette.authentication import AuthenticationBackend, AuthenticationError, AuthCredentials, SimpleUser
from starlette.middleware.authentication import AuthenticationMiddleware

from fastapi_authz import CasbinMiddleware


def get_examples(path):
    examples_path = os.path.split(os.path.realpath(__file__))[0] + "/../examples/"
    return os.path.abspath(examples_path + path)


class BasicAuth(AuthenticationBackend):
    async def authenticate(self, request):
        if "Authorization" not in request.headers:
            return None

        auth = request.headers["Authorization"]
        try:
            scheme, credentials = auth.split()
            decoded = base64.b64decode(credentials).decode("ascii")
        except (ValueError, UnicodeDecodeError, binascii.Error):
            raise AuthenticationError("Invalid basic auth credentials")

        username, _, password = decoded.partition(":")
        return AuthCredentials(["authenticated"]), SimpleUser(username)


@pytest.fixture
def app_fixture():
    enforcer = casbin.Enforcer(get_examples("rbac_model.conf"), get_examples("rbac_policy.csv"))

    app = FastAPI()

    app.add_middleware(CasbinMiddleware, enforcer=enforcer)
    app.add_middleware(AuthenticationMiddleware, backend=BasicAuth())

    yield app

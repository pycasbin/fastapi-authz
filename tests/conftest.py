import base64
import binascii
import os
from typing import Optional, Tuple, Union

import casbin
import jwt
import pytest
from fastapi import FastAPI
from starlette.authentication import (
    AuthenticationBackend, AuthenticationError, BaseUser, AuthCredentials)
from starlette.authentication import SimpleUser
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


class JWTUser(BaseUser):
    def __init__(self, username: str, token: str, payload: dict) -> None:
        self.username = username
        self.token = token
        self.payload = payload

    @property
    def is_authenticated(self) -> bool:
        return True

    @property
    def display_name(self) -> str:
        return self.username


class JWTAuthenticationBackend(AuthenticationBackend):

    def __init__(self,
                 secret_key: str,
                 algorithm: str = 'HS256',
                 prefix: str = 'Bearer',
                 username_field: str = 'username',
                 audience: Optional[str] = None,
                 options: Optional[dict] = None) -> None:
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.prefix = prefix
        self.username_field = username_field
        self.audience = audience
        self.options = options or dict()

    @classmethod
    def get_token_from_header(cls, authorization: str, prefix: str) -> str:
        """Parses the Authorization header and returns only the token"""
        try:
            scheme, token = authorization.split()
        except ValueError as e:
            raise AuthenticationError('Could not separate Authorization scheme and token') from e

        if scheme.lower() != prefix.lower():
            raise AuthenticationError(f'Authorization scheme {scheme} is not supported')
        return token

    async def authenticate(self, request) -> Union[None, Tuple[AuthCredentials, BaseUser]]:
        if "Authorization" not in request.headers:
            return None

        auth = request.headers["Authorization"]
        token = self.get_token_from_header(authorization=auth, prefix=self.prefix)
        try:
            payload = jwt.decode(token, key=self.secret_key, algorithms=self.algorithm, audience=self.audience,
                                 options=self.options)
        except jwt.InvalidTokenError as e:
            raise AuthenticationError(str(e)) from e
        return AuthCredentials(["authenticated"]), JWTUser(username=payload[self.username_field], token=token,
                                                           payload=payload)


@pytest.fixture
def jwt_app_fixture():
    JWT_SECRET_KEY = "secret"
    enforcer = casbin.Enforcer(get_examples("rbac_model.conf"), get_examples("rbac_policy.csv"))

    app = FastAPI()

    app.add_middleware(CasbinMiddleware, enforcer=enforcer)
    app.add_middleware(AuthenticationMiddleware, backend=JWTAuthenticationBackend(secret_key=JWT_SECRET_KEY))

    yield app

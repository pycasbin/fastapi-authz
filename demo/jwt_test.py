from datetime import datetime, timedelta
from typing import Optional, Tuple, Union

import casbin
import jwt
import uvicorn
from fastapi import FastAPI
from starlette.authentication import (
    AuthenticationBackend, AuthenticationError, BaseUser, AuthCredentials)
from starlette.middleware.authentication import AuthenticationMiddleware

from fastapi_authz import CasbinMiddleware

JWT_SECRET_KEY = "secret"
app = FastAPI()


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


enforcer = casbin.Enforcer('../examples/rbac_model.conf', '../examples/rbac_policy.csv')
app.add_middleware(CasbinMiddleware, enforcer=enforcer)

app.add_middleware(AuthenticationMiddleware, backend=JWTAuthenticationBackend(secret_key=JWT_SECRET_KEY))


def create_access_token(subject: str, expires_delta: timedelta = None) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=60
        )
    to_encode = {"exp": expire, "username": subject}
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm="HS256")


@app.get('/')
async def index():
    return "If you see this, you have been authenticated."


@app.get('/dataset1/protected')
async def auth_test():
    return "You must be alice to see this."


if __name__ == '__main__':
    print("alice:", create_access_token("alice", expires_delta=timedelta(minutes=60)))
    print("mark:", create_access_token("mark", expires_delta=timedelta(minutes=60)))
    uvicorn.run(app, debug=True)
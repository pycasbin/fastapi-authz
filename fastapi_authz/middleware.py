import typing

from casbin.enforcer import Enforcer

from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.status import HTTP_403_FORBIDDEN
from starlette.types import ASGIApp, Receive, Scope, Send


class CasbinMiddleware:
    """
    Middleware for Casbin
    """

    def __init__(
            self,
            app: ASGIApp,
            enforcer: Enforcer,
            token_loc: str = 'Header',
            token_key: str = 'X-Token',
            token_decode: typing.Callable = None
    ) -> None:
        """
        Configure Casbin Middleware

        :param app:Retain for ASGI.
        :param enforcer:Casbin Enforcer, must be initialized before FastAPI start.
        :param auth_type:Use auth or not.Usually,auth was provided by other middleware which implement
        AuthenticationMiddleware.
        :param token_loc:Where to find "Token" string.
        :param token_key:Correspond key for custom "Token" location.
        """
        self.app = app
        self.enforcer = enforcer
        self.user_loc = token_loc
        self.user_key = token_key

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] not in ("http", "websocket"):
            await self.app(scope, receive, send)
            return

        if self._enforce(scope, receive):
            await self.app(scope, receive, send)
            return
        else:
            response = JSONResponse(
                status_code=HTTP_403_FORBIDDEN,
                content="Forbidden"
            )

            await response(scope, receive, send)
            return

    def _enforce(self, scope: Scope, receive: Receive) -> bool:
        """
        Enforce a request

        :param user: user will be sent to enforcer
        :param request: ASGI Request
        :return: Enforce Result
        """

        request = Request(scope, receive)

        path = request.url.path
        method = request.method
        if 'user' not in scope:
            raise RuntimeError("Casbin Middleware must work with a Authentication Middleware")
        user = request.user
        return self.enforcer.enforce(user, path, method)

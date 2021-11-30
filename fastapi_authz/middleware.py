from casbin.enforcer import Enforcer
from starlette.authentication import BaseUser
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
    ) -> None:
        """
        Configure Casbin Middleware

        :param app:Retain for ASGI.
        :param enforcer:Casbin Enforcer, must be initialized before FastAPI start.
        """
        self.app = app
        self.enforcer = enforcer

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] not in ("http", "websocket"):
            await self.app(scope, receive, send)
            return

        if self._enforce(scope, receive) or scope["method"] == "OPTIONS":
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
            raise RuntimeError("Casbin Middleware must work with an Authentication Middleware")

        assert isinstance(request.user, BaseUser)

        user = request.user.display_name if request.user.is_authenticated else 'anonymous'

        return self.enforcer.enforce(user, path, method)

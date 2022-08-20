from datetime import datetime, timedelta

import jwt
import pytest
from starlette.testclient import TestClient


@pytest.mark.parametrize(
    "test_server_path, test_client_path, method, status_code, user, response_body", [
        ('/dataset1/resource2', '/dataset1/resource2', 'GET', 200, 'alice', 'ok'),
        ('/dataset1/resource2', '/dataset1/resource2', 'GET', 403, 'notalice', 'Forbidden'),
        ('/dataset1/resource2', '/dataset1/resource2', 'OPTIONS', 200, 'notalice', 'ok'),
        ('/dataset1/resource1', '/dataset1/resource1', 'POST', 200, 'alice', 'ok'),
    ]
)
def test_jwt_middleware_authed(jwt_app_fixture, test_server_path, test_client_path, method, status_code, user,
                               response_body):
    @getattr(jwt_app_fixture, method.lower())(test_server_path)
    async def index():
        return 'ok'

    JWT_SECRET_KEY = "secret"
    test_client = TestClient(jwt_app_fixture)
    expire = datetime.utcnow() + timedelta(
        minutes=60
    )
    token = jwt.encode({"exp": expire, "username": user}, JWT_SECRET_KEY, algorithm="HS256")

    test_response = getattr(test_client, method.lower())(test_client_path, headers={'Authorization': 'Bearer ' + token})

    assert test_response.status_code == status_code
    assert test_response.json() == response_body


@pytest.mark.parametrize(
    "test_server_path, test_client_path, method, status_code, response_body", [
        ('/login', '/login', 'GET', 200, 'ok'),
        ('/', '/', 'GET', 200, 'ok')
    ]
)
def test_jwt_middleware_not_authed(jwt_app_fixture, test_server_path, test_client_path, method, status_code,
                                   response_body):
    @getattr(jwt_app_fixture, method.lower())(test_server_path)
    async def index():
        return 'ok'

    test_client = TestClient(jwt_app_fixture)

    test_response = getattr(test_client, method.lower())(test_client_path)

    assert test_response.status_code == status_code
    assert test_response.json() == response_body


if __name__ == '__main__':
    pytest.main()

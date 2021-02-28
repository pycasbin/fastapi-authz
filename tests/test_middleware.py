import pytest
from fastapi import Depends
from starlette.authentication import requires
from starlette.testclient import TestClient


@pytest.mark.parametrize(
    "test_server_path, test_client_path, method, status_code, user, response_body", [
        ('/dataset1/resource2', '/dataset1/resource2', 'GET', 200, 'alice', 'ok'),
    ]
)
def test_middleware_authed(app_fixture, test_server_path, test_client_path, method, status_code, user, response_body):
    # if method == 'GET':
    #     @app_fixture.get(test_server_path)
    #     async def index():
    #         return 'ok'
    # elif method == 'POST':
    #     @app_fixture.post(test_server_path)
    #     async def index():
    #         return 'ok'
    # elif method == 'PUT':
    #     @app_fixture.put(test_server_path)
    #     async def index():
    #         return 'ok'

    @getattr(app_fixture, method.lower())(test_server_path)
    async def index():
        return 'ok'

    test_client = TestClient(app_fixture)

    test_response = test_client.get(test_client_path, auth=(user, 'password'))

    assert test_response.status_code == status_code
    assert test_response.json() == response_body


if __name__ == '__main__':
    pytest.main()

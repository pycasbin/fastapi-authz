# fastapi-authz

[![Build Status](https://github.com/pycasbin/fastapi-authz/actions/workflows/release.yml/badge.svg)](https://github.com/pycasbin/fastapi-authz/actions/workflows/release.yml)
[![Coverage Status](https://coveralls.io/repos/github/pycasbin/fastapi-authz/badge.svg)](https://coveralls.io/github/pycasbin/fastapi-authz)
[![Version](https://img.shields.io/pypi/v/fastapi-authz.svg)](https://pypi.org/project/fastapi-authz/)
[![PyPI - Wheel](https://img.shields.io/pypi/wheel/fastapi-authz.svg)](https://pypi.org/project/fastapi-authz/)
[![Pyversions](https://img.shields.io/pypi/pyversions/fastapi-authz.svg)](https://pypi.org/project/fastapi-authz/)
[![Download](https://img.shields.io/pypi/dm/fastapi-authz.svg)](https://pypi.org/project/fastapi-authz/)
[![Gitter](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/casbin/lobby)

fastapi-authz is an authorization middleware for [FastAPI](https://fastapi.tiangolo.com/), it's based
on [PyCasbin](https://github.com/casbin/pycasbin).

## Installation

Install from pip

```bash
pip install fastapi-authz
```

Clone this repo

```bash
git clone https://github.com/pycasbin/fastapi-authz.git
python setup.py install
```

## Quickstart

This middleware is designed to work with another middleware which implement `AuthenticationMiddleware` interface.

```python
import base64
import binascii

import casbin

from fastapi import FastAPI
from starlette.authentication import AuthenticationBackend, AuthenticationError, SimpleUser, AuthCredentials
from starlette.middleware.authentication import AuthenticationMiddleware

from fastapi_authz import CasbinMiddleware

app = FastAPI()


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


enforcer = casbin.Enforcer('../examples/rbac_model.conf', '../examples/rbac_policy.csv')

app.add_middleware(CasbinMiddleware, enforcer=enforcer)
app.add_middleware(AuthenticationMiddleware, backend=BasicAuth())


@app.get('/')
async def index():
    return "If you see this, you have been authenticated."


@app.get('/dataset1/protected')
async def auth_test():
    return "You must be alice to see this."
```

- anonymous request

```bash
curl -i http://127.0.0.1:8000/dataset1/protected
```

```bash
HTTP/1.1 403 Forbidden
date: Mon, 01 Mar 2021 09:00:08 GMT
server: uvicorn
content-length: 11
content-type: application/json

"Forbidden"
```

- authenticated request

```bash
curl -i -u alice:password http://127.0.0.1:8000/dataset1/protected
```

```bash
HTTP/1.1 200 OK
date: Mon, 01 Mar 2021 09:04:54 GMT
server: uvicorn
content-length: 32
content-type: application/json

"You must be alice to see this."
```

It used the casbin config from `examples` folder, and you can find this demo in `demo` folder.

You can also view the unit tests to understand this middleware.

Besides, there is another example for `CasbinMiddleware` which is designed to work with JWT authentication. You can find
it in `demo/jwt_test.py`.

## Development

### Run unit tests

1. Fork/Clone repository
2. Install fastapi-authz dependencies, and run `pytest`

```bash
pip install -r dev_requirements.txt
pip install -r requirements.txt
pytest
```

### Update requirements with pip-tools

```bash
# update requirements.txt
pip-compile --no-annotate --no-header --rebuild requirements.in
# sync venv
pip-sync
```

### Manually Bump Version

```
bumpversion major  # major release
or
bumpversion minor  # minor release
or
bumpversion patch  # hotfix release
```

## Documentation

The authorization determines a request based on ``{subject, object, action}``, which means what ``subject`` can perform
what ``action`` on what ``object``. In this plugin, the meanings are:

1. ``subject``: the logged-in user name
2. ``object``: the URL path for the web resource like `dataset1/item1`
3. ``action``: HTTP method like GET, POST, PUT, DELETE, or the high-level actions you defined like "read-file", "
   write-blog" (currently no official support in this middleware)

For how to write authorization policy and other details, please refer
to [the Casbin's documentation](https://casbin.org).

## Getting Help

- [Casbin](https://casbin.org)

## License

This project is under Apache 2.0 License. See the [LICENSE](LICENSE) file for the full license text.

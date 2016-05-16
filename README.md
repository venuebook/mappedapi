## Mapped API ##

[![Build Status](https://travis-ci.com/venuebook/mappedapi.svg?token=j1A1J2RZ8nCwcqmzbYLx&branch=master)](https://travis-ci.com/venuebook/mappedapi)

A python library for an easily mapped RESTful API.

**Installation:**

(unless performing a system wide install, it's recommended to install inside of a virtualenv)

```bash
# Install dependencies:
pip install -r requirements.txt # Install core & tests
pip install -r requirements/core.txt # Just install core dependencies
pip install -r requirements/tests.txt # Install test dependencies

# Install mappedapi
python setup.py install
```

**Usage:**

```python
## example/__init__.py

## example/client.py
import mappedapi.base
from example.api import APIResource

class Client(object):
    RESOURCE_CLASS = APIResource
    def __init__(self, access_token):
        self.auth = {'token': access_token}

## example/settings.py
API_BASE_URL = 'https://www.example.com/api/'
API_VERSION = '3'

## example/mapping.py
RESOURCE_MAPPING = {
    'dogs': {
        {'shibes':
            'get': {
                # https://www.example.com/api/3/dogs/{dog_id}/shibes
                'endpoint_base': ['dogs', 'shibes'],
                'ids': ['dog_id'],
                'verb': 'get',
            },
            'post': {
                # https://www.example.com/api/3/dogs/{dog_id}/shibes
                'endpoint_base': ['dogs', 'shibes'],
                'ids': ['dog_id'],
                'verb': 'post',
            },
        },
    },
}
## example/api.py
import mappedapi.base
from example import mapping
from example import settings

class APIResourceItem(mappedapi.base.APIResourceItem):
    """Item in a APIResource - Either a nested resource or an action."""

    def _get_base_url(self):
        return '%s/%s' % (settings.API_BASE_URL, settings.API_VERSION)

    def _get_headers(self):
        return {
            'Authorization': 'Bearer %s' % self.auth['token'],
        }

    def _process_call_arguments(self, kwargs):
        if 'operations' in kwargs:
            data = []
            for operation in kwargs['operations']:
                data.append({'operation': operation[0], 'property': operation[1], 'value': operation[2]})
            kwargs['data'] = data
        return kwargs

class APIResource(mappedapi.base.APIResource):
    """Top Level API Resource"""

    ITEM_CLASS = APIResourceItem
    RESOURCE_MAPPING = mapping.RESOURCE_MAPPING

## run.py

import uuid
from example.client import Client

# Initialize the client.
client = Client(YOUR_ACCESS_TOKEN)

print(client.dogs.shibes.get(dog_id='10203').json())

client.dogs.shibes.post(dog_id='10203', data={'name':'Doctor Wow'})
```

**Tests:**

```
py.test mappedapi --cov=mappedapi
```

**Dependencies:**

Core library depends on ``requests``.

Tests depend on ``pytest, pytest-cov, responses``.

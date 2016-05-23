import json
import pytest
import responses
import mappedapi.base

"""
Test basic functionality of MappedAPI with an example implementation.
"""

########################
# TEST DATA
########################

BASE_URL = 'http://localhost'

TEST_DOG_ID = '1'
TEST_DOG = {
    'name': 'Doctor Woof',
    'bark': 'loud',
    'doge': 'wow',
}

########################
# TEST IMPLEMENTATION
########################

RESOURCE_MAPPING = {
    'dogs': {
        'shibes': {
            'get': {
                'endpoint_base': ['dogs', 'shibes'],
                'endpoint_ids': ['dog_id'],
                'verb': 'get',
            },
            'post': {
                'endpoint_base': ['dogs', 'shibes'],
                'endpoint_ids': ['dog_id'],
                'required_args': ['name'],
                'verb': 'post',
            },
        },
    },
}

class APIResource(mappedapi.base.APIResource):
    """Item in a APIResource - Either a nested resource or an action."""

    def _get_base_url(self):
        return BASE_URL

    def _get_headers(self):
        return {
            'Authorization': 'Bearer %s' % self.auth['token'],
        }

class Client(mappedapi.base.Client):
    RESOURCE_CLASS = APIResource
    RESOURCE_MAPPING = RESOURCE_MAPPING

    def __init__(self, access_token):
        super(Client, self).__init__()
        self.auth = {'token': access_token}

########################
# TESTS
########################

@pytest.fixture(scope="module")
def client():
    """Setup RequestHandler instance with test values."""
    return Client('Token')

def test_getattr_auth():
    """Test getting an attribute that does exist."""
    assert('token' in client().auth)

def test_getattr_error_api_resource():
    """Test getting an attribute that doesn't exist."""
    with pytest.raises(AttributeError) as exception_info:
        client().dogs.wow
    assert(exception_info.typename == 'AttributeError')

def test_getattr_error_api_resource_item():
    """Test getting an attribute that doesn't exist."""
    with pytest.raises(AttributeError) as exception_info:
        client().dogs.shibes.wow
    assert(exception_info.typename == 'AttributeError')

def test_getattr_error_client():
    """Test getting an attribute that doesn't exist."""
    with pytest.raises(AttributeError) as exception_info:
        client().wow
    assert(exception_info.typename == 'AttributeError')

@responses.activate
def test_request_error():
    """Test client.users.get request error"""
    responses.add(method=responses.GET,
        url='%s/dogs/%s/shibes' % (BASE_URL, TEST_DOG_ID),
        body=json.dumps(TEST_DOG),
        status=400,
        content_type='application/json'
        )
    with pytest.raises(Exception) as exception_info:
        r = client().dogs.shibes.get(dog_id=TEST_DOG_ID)
    assert exception_info.typename == 'MappedAPIRequestError'

def test_validation_error():
    """Test client.users.post validation error"""
    with pytest.raises(Exception) as exception_info:
        r = client().dogs.shibes.post(dog_id=TEST_DOG_ID, data={'bark':'loud'})
    assert exception_info.typename == 'MappedAPIValidationError'

@responses.activate
def test_endpoint_get():
    """Test client.users.badge.get"""
    print('%s/dogs/%s/shibes' % (BASE_URL, TEST_DOG_ID))
    responses.add(method=responses.GET,
        url='%s/dogs/%s/shibes' % (BASE_URL, TEST_DOG_ID),
        body=json.dumps(TEST_DOG),
        status=200,
        content_type='application/json'
        )
    r = client().dogs.shibes.get(dog_id=TEST_DOG_ID)
    assert r.status_code == 200

@responses.activate
def test_endpoint_post():
    """Test client.users.create"""
    responses.add(method=responses.POST,
        url='%s/dogs/%s/shibes' % (BASE_URL, TEST_DOG_ID),
        body=json.dumps(TEST_DOG),
        status=201,
        content_type='application/json'
        )
    r = client().dogs.shibes.post(dog_id=TEST_DOG_ID, data=TEST_DOG)
    assert r.status_code == 201

import itertools
import requests
from mappedapi.exceptions import MappedAPIRequestError

class APIResource(object):
    """Top Level API Resource"""

    ITEM_CLASS = None
    RESOURCE_MAPPING = []

    def __init__(self, auth, items):
        self.auth = auth
        self.items = items

    @classmethod
    def map(cls, auth, resource):
        """ Instantiate APIResource with Client authorization from resource name.
        :param dict auth: Client authorization.
        :param string resource: Resource name.
        :return: API Resource
        :rtype: ``APIResource``
        """
        if not resource in cls.RESOURCE_MAPPING:
            return None
        return cls(auth=auth, items=cls.RESOURCE_MAPPING[resource])

    def __getattr__(self, attr):
        """getattr override to allow calling actions and nested resources eg client.users"""
        if not self.__class__.ITEM_CLASS:
            raise Exception('Error: APIResource.ITEM_CLASS not set.')
        if attr in self.items:
            return self.__class__.ITEM_CLASS(self.auth, self.items[attr])
        return self.__getattribute__(attr)

class APIResourceItem(object):
    """Item in a APIResource - Either a nested resource or an action."""

    def __init__(self, auth, action):
        self.auth = auth
        if ('verb' not in action): # No HTTP verb - this is a nested action.
            self.nested_actions = action
            return
        self.nested_actions = []
        self.endpoint_base = action['endpoint_base']
        self.ids = action['ids']
        self.verb = action['verb']

    def __call__(self, **kwargs):        
        """Perform a http request via the specified method to an API endpoint.
        :param kwargs kwargs: Keyword arguments:
            ids (navigation ids for data types (conversations, forms, etc),
            data={} # post/put/patch data
            params={} # get data
        :return: Response
        :rtype: ``Response``
        """
        kwargs = self._process_call_arguments(kwargs)
        # Post Data
        data = kwargs['data'] if ('data' in kwargs) else None
        # Params
        params = kwargs['params'] if ('params' in kwargs) else None
        # Headers
        headers = self._get_headers()
        # Ids
        ids = [kwargs[id_arg] for id_arg in self.ids if id_arg in kwargs] if (self.ids) else None
        if ids:
            endpoint = '/'.join(list(next(i) for i in itertools.cycle([iter(self.endpoint_base), iter(ids)])))
        else:
            endpoint = '/'.join(self.endpoint_base)
        # URL
        url = '%s/%s' % (self._get_base_url(), endpoint)
        # Request
        response = requests.__getattribute__(self.verb)(
            url=url,
            headers=headers,
            json=data,
            params=params,
        )
        if response.status_code >= 300:
            try:
                response.raise_for_status()
            except requests.exceptions.HTTPError as e:
                raise MappedAPIRequestError(request=e.request, response=e.response)
        return response

    def __getattr__(self, attr):
        """getattr override to allow calling nested resources eg client.users.badge"""
        if attr in self.nested_actions:
            return self.__class__(self.auth, self.nested_actions[attr])
        return self.__getattribute__(attr)

    def _get_base_url(self):
        """Get base API url.

        :return: base app url
        :rtype: ``string``
        """
        raise Exception('Error: _get_base_url is not implemented.')

    def _get_headers(self):
        """Get Headers (Including "Authorization") for requests.

        :return: headers.
        :rtype: ``dict``
        """
        raise Exception('Error: _get_headers is not implemented.')

    def _process_call_arguments(self, kwargs):
        """Optionally process the kwargs before proceeding.
        For example, add a kwarg "operations" and condense it into a format to be posted as "data".

        :return: kwargs
        :rtype: ``kwargs``
        """
        return kwargs


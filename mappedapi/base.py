import itertools
import requests
from mappedapi import settings
from mappedapi.exceptions import MappedAPIRequestError, MappedAPIValidationError

class APIResource(object):
    """Either a nested resource or an API action."""

    def __init__(self, auth, children):
        """Initialize

        :param dict auth: Client authorization.
        :param dict children: Mapping.
        """
        self.auth = auth
        if ('verb' not in children): # No HTTP verb - this is nested.
            self.nested_children = children
            return
        self.nested_children = []
        self.endpoint_base = children['endpoint_base']
        self.endpoint_ids = children['endpoint_ids']
        self.required_args = children['required_args'] if ('required_args' in children) else None
        self.verb = children['verb'].lower()

    @classmethod
    def map(cls, auth, resource, resource_mapping):
        """ Instantiate APIResource with Client authorization from resource name.
        :param dict auth: Client authorization.
        :param string resource: Resource name.
        :param dict resource_mapping: Resource mapping.
        :return: API Resource
        :rtype: ``APIResource``
        """
        if not resource in resource_mapping:
            return None
        return cls(auth=auth, children=resource_mapping[resource])

    def __call__(self, **kwargs):        
        """Perform a http request via the specified method to an API endpoint.
        :param kwargs kwargs: Keyword arguments:
            endpoint_ids (navigation endpoint_ids for data types (conversations, forms, etc),
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
        if self.required_args:
            target = params if (self.verb == 'get') else data
            missing = []
            for arg in self.required_args:
                if not arg in target:
                    missing.append(arg)
            if missing:
                raise MappedAPIValidationError(
                    message='Missing required arguments: %s' % ','.join(missing)
                )
        # Headers
        headers = self._get_headers()
        # Ids
        endpoint_ids = [kwargs[id_arg] for id_arg in self.endpoint_ids if id_arg in kwargs] if (self.endpoint_ids) else None
        if endpoint_ids:
            endpoint = '/'.join(list(next(i) for i in itertools.cycle([iter(self.endpoint_base), iter(endpoint_ids)])))
        else:
            endpoint = '/'.join(self.endpoint_base)
        # URL
        url = '%s/%s' % (self._get_base_url(), endpoint)
        # Request
        response = requests.__getattribute__(self.verb)(
            url=url,
            hooks=settings.REQUEST_HOOK,
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
        if attr in self.nested_children:
            return self.__class__(self.auth, self.nested_children[attr])
        raise AttributeError("'APIResource' object has no attribute '%s'" % attr)

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

class Client(object):
    """Base object for API Client."""

    RESOURCE_CLASS = None
    RESOURCE_MAPPING = []

    def __init__(self):
        """Initialize Client.

        Override and provide call to super:

        super(Client).__init__(self)"""
        if not self.__class__.RESOURCE_CLASS:
            raise Exception('Error: Client.RESOURCE_CLASS not set.')
        if not self.__class__.RESOURCE_MAPPING:
            raise Exception('Error: Client.RESOURCE_MAPPING not set.')

    def __getattr__(self, attr):
        """getattr override to allow calling API Resources eg client.users"""
        resource = self.RESOURCE_CLASS.map(self.auth, attr, self.__class__.RESOURCE_MAPPING)
        if not resource:
            raise AttributeError("'Client' object has no attribute '%s'" % attr)
        return resource



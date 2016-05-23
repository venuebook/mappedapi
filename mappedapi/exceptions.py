class MappedAPIRequestError(Exception):
    """Wraps requests.exceptions.HTTPError for convenience and give a little more info in the message."""

    def __init__(self, request, response):
        """
        :param Request request: requests.Request.
        :param Response response: responses.Response.
        """
        body = ''
        if request.method in ('POST', 'PUT', 'PATCH') and request.body:
            body = '\nRequest Body: %s' % request.body
        headers = request.headers
        headers.pop('Authorization')
        # Message leaves out request.headers['Authorization'] for security reasons.
        # This can be accessed via the exception:
        # exception_instance.request.headers['Authorization']
        message = 'Response: %(status_code)s: %(reason)s\nRequest: %(method)s %(url)s\nRequest Headers:%(headers)s%(body)s%(content)s' % {
            'body': body,
            'content': ('\nResponse Content:\n%s' % response.content) if response.content else '',
            'headers': headers,
            'method': request.method,
            'reason': response.reason,
            'status_code': response.status_code,
            'url': request.url,
        }
        super(MappedAPIRequestError, self).__init__(message)
        self.message = message
        self.request = request
        self.response = response

class MappedAPIValidationError(Exception):
    """Validation error."""

    def __init__(self, message):
        """
        :param string message: Error message.
        """
        super(MappedAPIValidationError, self).__init__(message)
        self.message = message
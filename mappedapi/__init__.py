from mappedapi import settings

def set_request_hook(func):
    """Sets a function to execute on requests made by mappedapi via the requests model.

    Accepts arguments (response, *args, **kwargs).

    :param function func: Function to execute on request.
    """
    settings.REQUEST_HOOK = {'response':func} if func else {}
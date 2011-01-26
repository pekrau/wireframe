""" wireframe: Minimalistic Web Resource Framework built on Python WSGI.

Processor for handling a session id.

Per Kraulis
2009-10-31
"""

import uuid


class SessionProcessor(object):
    """Processor for getting and setting an opaque session identifier.
    The identifier attribute with the given key is set in the response
    instance. The value is retrieved from the cookie if present, or it
    is set to a new value, which simultaneously sets the cookie.
    The value is a randomly generated UUID."""

    def __init__(self, key='sessionid', path=None):
        self.key = key
        self.path = path

    def __call__(self, request, response):
        self.response = response
        try:
            morsel = request.cookie[self.key]
            setattr(self.response, self.key, morsel.value)
        except KeyError:
            value = self.get_value(request)
            setattr(self.response, self.key, value)
            self.response.headers.cookie[self.key] = value
            if self.path:
                self.response.headers.cookie[self.key]['path'] = self.path

    def get_value(self, request):
        "Return a session identifier value."
        return str(uuid.uuid4())

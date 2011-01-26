""" wireframe: Minimalistic Web Resource Framework built on Python WSGI.

Processor for basic authentication.

Per Kraulis
2009-10-31
"""

import base64

from .response import HTTP_UNAUTHORIZED_BASIC_CHALLENGE


def decode(request):
    """Return tuple (user, password) given by request basic authentication.
    Raises ValueError if no basic authentication given."""
    try:
        auth_type, coded = request.headers['Authorization'].split()
    except KeyError:
        raise ValueError('no Authorization header given')
    if auth_type != 'Basic':
        raise ValueError('not Basic Authorization')
    decoded = base64.standard_b64decode(coded)
    return decoded.split(":", 1)


class BasicAuthenticate(object):
    """Processor class for performing basic authentication.
    The user and password is set as members in the Request instance."""

    def __init__(self, realm, require=True):
        self.realm = realm
        self.require = require

    def __call__(self, request, response):
        try:
            user, password = decode(request)
            self.set_login(request, response, user, password)
        except ValueError:
            if self.require:
                raise HTTP_UNAUTHORIZED_BASIC_CHALLENGE(realm=self.realm)

    def set_login(self, request, response, user=None, password=None):
        """Set the resulting user and password as members in the request.
        If the user and/or password is incorrect, then raise ValueError.
        By default, no checking is performed.
        To be redefined by inheriting classes to provide checking logic."""
        request.user = user
        request.password = password

""" wireframe: Minimalistic Web Resource Framework built on Python WSGI.

HTTP response class and status classes.

Per Kraulis
2009-10-31
2011-01-26  added default response mimetype
"""

import httplib, exceptions

from .headers import Headers


class Response(object):
    """Basic response class.
    HTTP header items are accessed through dictionary-like calls.
    The body data is set using 'append' and is read by iterating
    over the instance.
    Cleanup operation(s) to be called after the request has been
    processed may be appended as callables (taking no arguments)
    to the member list 'cleanup'."""

    http_code = httplib.OK      # Default; may be redefined
    content_type = 'text/plain' # Default; may be redefined

    def __init__(self):
        self.headers = Headers()
        self.headers['content-type'] = self.content_type
        self.body = []
        self.cleanup = []       # Callable instances called on 'close'

    def __str__(self):
        return "%s %s" % (self.http_code, httplib.responses[self.http_code])

    def __getitem__(self, key):
        return self.headers[key]

    def __setitem__(self, key, value):
        self.headers[key] = value

    def get(self, key, default=None):
        return self.headers.get(key, default=default)

    def __delitem__(self, key):
        del self.headers[key]

    def __iter__(self):
        "Return an iterator over the items in the body."
        return iter([str(i) for i in self.body])

    def __del__(self):
        self.close()

    def append(self, data):
        self.body.append(data)

    def close(self):
        while self.cleanup:
            func = self.cleanup.pop()
            func()


class HTTP_STATUS(Response, exceptions.Exception):
    "Base class for HTTP errors; also a Response subclass."

    def __init__(self, remark='', **kwargs):
        super(HTTP_STATUS, self).__init__()
        self.remark = remark
        for key in kwargs:
            self.headers[key] = kwargs[key]


class HTTP_SUCCESS(HTTP_STATUS):
    pass

class HTTP_OK(HTTP_SUCCESS):
    http_code = httplib.OK

class HTTP_CREATED(HTTP_SUCCESS):
    http_code = httplib.CREATED

class HTTP_ACCEPTED(HTTP_SUCCESS):
    http_code = httplib.ACCEPTED

class HTTP_NO_CONTENT(HTTP_SUCCESS):
    http_code = httplib.NO_CONTENT


class HTTP_REDIRECTION(HTTP_STATUS):
    pass

class HTTP_MOVED_PERMANENTLY(HTTP_REDIRECTION):
    http_code = httplib.MOVED_PERMANENTLY

class HTTP_FOUND(HTTP_REDIRECTION):
    http_code = httplib.FOUND

class HTTP_SEE_OTHER(HTTP_REDIRECTION):
    http_code = httplib.SEE_OTHER

class HTTP_NOT_MODIFIED(HTTP_REDIRECTION):
    http_code = httplib.NOT_MODIFIED

class HTTP_TEMPORARY_REDIRECT(HTTP_REDIRECTION):
    http_code = httplib.TEMPORARY_REDIRECT


class HTTP_ERROR(HTTP_STATUS):
    pass


class HTTP_CLIENT_ERROR(HTTP_ERROR):
    pass

class HTTP_BAD_REQUEST(HTTP_CLIENT_ERROR):
    http_code = httplib.BAD_REQUEST

class HTTP_UNAUTHORIZED(HTTP_CLIENT_ERROR):
    http_code = httplib.UNAUTHORIZED

class HTTP_UNAUTHORIZED_BASIC_CHALLENGE(HTTP_UNAUTHORIZED):
    def __init__(self, remark=None, **kwargs):
        realm = kwargs.pop('realm', 'unspecified')
        super(HTTP_UNAUTHORIZED_BASIC_CHALLENGE,
              self).__init__(remark=remark, **kwargs)
        self.headers['www-authenticate'] = 'Basic realm="%s"' % realm

class HTTP_FORBIDDEN(HTTP_CLIENT_ERROR):
    http_code = httplib.FORBIDDEN

class HTTP_NOT_FOUND(HTTP_CLIENT_ERROR):
    http_code = httplib.NOT_FOUND

class HTTP_METHOD_NOT_ALLOWED(HTTP_CLIENT_ERROR):
    http_code = httplib.METHOD_NOT_ALLOWED

class HTTP_NOT_ACCEPTABLE(HTTP_CLIENT_ERROR):
    http_code = httplib.NOT_ACCEPTABLE

class HTTP_REQUEST_TIMEOUT(HTTP_CLIENT_ERROR):
    http_code = httplib.REQUEST_TIMEOUT

class HTTP_CONFLICT(HTTP_CLIENT_ERROR):
    http_code = httplib.CONFLICT

class HTTP_GONE(HTTP_CLIENT_ERROR):
    http_code = httplib.GONE


class HTTP_SERVER_ERROR(HTTP_ERROR):
    pass

class HTTP_INTERNAL_SERVER_ERROR(HTTP_SERVER_ERROR):
    http_code = httplib.INTERNAL_SERVER_ERROR

class HTTP_NOT_IMPLEMENTED(HTTP_SERVER_ERROR):
    http_code = httplib.NOT_IMPLEMENTED

class HTTP_SERVICE_UNAVAILABLE(HTTP_SERVER_ERROR):
    http_code = httplib.SERVICE_UNAVAILABLE

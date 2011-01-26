""" wireframe: Minimalistic Web Resource Framework built on Python WSGI.

Base Dispatcher class, to be elaborated.

Per Kraulis
2011-01-26
"""

from .application import HTTP_METHODS
from .response import HTTP_METHOD_NOT_ALLOWED, HTTP_NO_CONTENT


class BaseDispatcher(object):
    """Base Dispatcher class.
    Elaborate this class by implementing methods named for the
    HTTP request methods to be handled by this dispatcher. 
    The name of HTTP request method is used to identify the class
    method to call. That is, if the HTTP method is 'GET', then
    the class method 'GET' will be used to handle it.
    The class methods are given the Request and Response instances
    as arguments."""

    def __call__(self, request, response):
        """The name of HTTP request method is used to identify
        the class method to call. That is, if the HTTP method is 'GET',
        then the class method 'GET' will be used to handle it.
        The class methods are given the Request and Response instances
        as arguments."""
        try:
            method = getattr(self, request.http_method)
        except AttributeError:
            allowed = [m for m in HTTP_METHODS if hasattr(self, m)]
            raise HTTP_METHOD_NOT_ALLOWED(allow=','.join(allowed))
        self.prepare(request, response)
        method(request, response)

    def prepare(self, request, response):
        """Prepare this instance before executing the method
        corresponding to the HTTP request method.
        By default does nothing.
        To be redefined when required."""
        pass

    def OPTIONS(self, request, response):
        allowed = [m for m in HTTP_METHODS if hasattr(self, m)]
        raise HTTP_NO_CONTENT(allow=','.join(allowed))

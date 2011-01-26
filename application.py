""" wireframe: Minimalistic Web Resource Framework built on Python WSGI.

Application class for Python WSGI.

Per Kraulis
2009-10-31
2009-11-29  allow dispatcher class, in addition to method-processors maps
2010-01-20  added options for human-readable error and debug output
"""

import sys, re, traceback, cgi, logging

from .request import Request
from .response import (Response, HTTP_NOT_FOUND, HTTP_METHOD_NOT_ALLOWED,
                       HTTP_ERROR, HTTP_UNAUTHORIZED, HTTP_STATUS)


HTTP_METHODS = set(['GET', 'POST', 'PUT', 'DELETE', 'HEAD', 'OPTIONS'])


class Application(object):
    """An instance of this class handles HTTP requests by dispatching to
    processor(s) or dispatcher(s) according to the URL path and HTTP method.

    This is the interface to Python WSGI. An instance of this class
    (or a subclass of it) must be set as the module-level variable
    'application', as specified for your WSGI implementation.

    The 'path_matcher' specified in calls to 'add_class' and 'add_map'
    must be a callable or a regular expression string. If it is a callable,
    it must take one single string as argument, which is the URL path for
    the HTTP request. It must produce a non-False result on successful
    match. The result will be provided to the Request instance as
    attribute 'path_values'.

    If the URL path matcher is a string, it is compiled into a regexp,
    whose groups will be provided to the Request instance as 'path_values'
    (list of unnamed groups) and 'path_named_values' (dictionary of
    named groups)."""

    def __init__(self, human_error_output=True, human_debug_output=False):
        """Set error and debug output flags for when the user agent
        appears to represent a human user, i.e. a browser."""
        self.human_error_output = human_error_output
        self.human_debug_output = human_debug_output
        self.path_handlers = []  # Tuples (URL path matcher, handler),
                                 # where handler may be a processor class
                                 # or a dict(method=processor callables).

    def add_map(self, path_matcher, **method_map):
        """Add a URL path matcher with a dictionary having the HTTP method
        name as key and a (list of) processor function(s) as value.

        For valid 'path_matcher' values, see the documentation for this class.

        A processor is simply a callable which takes the Request instance
        and the Response instance as arguments. The processor may add
        attributes to instances input to it.

        A single processor, or a sequence (tuple or list) of processors,
        may be given for a given HTTP method."""
        if isinstance(path_matcher, basestring):
            path_matcher = re.compile(path_matcher)
        method_map = dict([(m.upper(), p) for m,p in method_map.items()])
        self.path_handlers.append((path_matcher, method_map))

    def add_class(self, path_matcher, dispatcher_class):
        """Add a URL path matcher with a dispatcher class.

        For valid 'path_matcher' values, see the documentation for this class.

        The dispatcher class must either be a callable, or it must provide
        the appropriate method(s) named for the HTTP methods it is to handle.
        Such a method will be called with the Request and Response instances
        as arguments."""
        assert isinstance(dispatcher_class, object)
        if isinstance(path_matcher, basestring):
            path_matcher = re.compile(path_matcher)
        self.path_handlers.append((path_matcher, dispatcher_class))

    def __call__(self, environ, start_response):
        """WSGI interface; this is called for each HTTP request.
        The HTTP request is dispatched to the appropriate processor or
        dispatcher by finding the correct URL path matcher (defined by
        previous calls to 'add_map' or 'add_class') for the given URL path
        and HTTP method.
        NOTE: The URL path value used for matching is taken from
        the PATH_INFO environment variable, thus excluding any path
        prefix for the virtual location of the Python WSGI application."""
        path = environ['PATH_INFO']
        logging.debug("wireframe: request URL path %s", path)
        try:
            for path_matcher, handler in self.path_handlers:
                if callable(path_matcher): # URL path matcher is callable
                    try:
                        path_values = path_matcher(path)
                    except ValueError:
                        pass
                    else:
                        if path_values:
                            path_named_values = dict()
                            break
                else:                     # URL path matcher is compiled regexp
                    m = path_matcher.match(path)
                    if m:
                        path_values = [g for (i,g) in enumerate(m.groups())
                                       if i+1 not in m.re.groupindex.values()]
                        path_named_values = m.groupdict()
                        break
            else:
                raise HTTP_NOT_FOUND("URL path: %s" % path)
            request = self.get_request(environ, path_values, path_named_values)
            logging.debug("wireframe: request HTTP method %s",
                          request.http_method)
            response = self.get_response()
            if isinstance(handler, dict): # Map: HTTP method to processor(s)
                try:
                    processors = handler[request.http_method]
                except KeyError:
                    allowed = handler.keys()
                    raise HTTP_METHOD_NOT_ALLOWED(allow=','.join(allowed))
                if isinstance(processors, (list, tuple)): # Seq of callables
                    for processor in processors:
                        processor(request, response)
                else:
                    processors(request, response) # Not a seq: single callable
            elif isinstance(handler, object):     # Dispatcher class
                processor = handler()
                if callable(processor):           # Does its own method dispatch
                    processor(request, response)
                else:
                    try:
                        method = getattr(processor, request.http_method)
                    except AttributeError:
                        allowed = [m for m in HTTP_METHODS
                                   if hasattr(processor, m)]
                        raise HTTP_METHOD_NOT_ALLOWED(allow=','.join(allowed))
                    method(request, response)
            else:
                raise HTTP_INTERNAL_SERVER_ERROR
        except HTTP_UNAUTHORIZED, response: # No logging, nor human output
            pass
        except HTTP_ERROR, response:
            try:
                http_method = request.http_method
                human_user_agent = request.human_user_agent
            except UnboundLocalError:
                http_method = '?'
                human_user_agent = '?'
            logging.debug("wireframe: '%s' %s: HTTP error %s %s",
                          path, http_method, response, response.remark)
            if self.human_error_output and human_user_agent:
                response = self.to_human_output("Error: %s" % response,
                                                response.remark)
        except HTTP_STATUS, response:
            logging.debug("wireframe: '%s' %s: HTTP status %s",
                          path, request.http_method, response)
        except Exception, message:
            tb = traceback.format_exc(limit=20)
            logging.error("wireframe: '%s' exception %s\n%s",
                          path, message, tb)
            if self.human_debug_output and request.human_user_agent:
                response = self.to_human_output('Internal error', tb)
            else:
                raise
        start_response(str(response), response.headers.items)
        return response

    def to_human_output(self, title, remark):
        "Convert the error remark to a human-readable HTML response."
        response = Response()
        response['content-type'] = 'text/html'
        response.append(
"""<html>
<head>
<title>%s</title>
<head>
<body>
<h1>%s</h1>
<pre>%s</pre>
</body>
</html>""" % (title, title, cgi.escape(remark)))
        return response

    def get_request(self, environ, path_values, path_named_values):
        """Return a Request instance.
        May be redefined to return an instance of a Request subclass."""
        return Request(environ, path_values, path_named_values)

    def get_response(self):
        """Return a Response instance.
        May be redefined to return an instance of a Response subclass."""
        return Response()

""" wireframe: Minimalistic Web Resource Framework built on Python WSGI.

Processor for producing debug log messages of items of the request.

Per Kraulis
2011-01-25  split out of response.py
"""


class DebugProcessor(object):
    "Log (at debug level) the values of items of the request."

    def __init__(self, title='Debug request',
                 path_values=True, environ=True, headers=True,
                 cookie=True, cgi_fields=True, user=True):
        self.title = title
        self.path_values = path_values
        self.environ = environ
        self.headers = headers
        self.cookie = cookie
        self.cgi_fields = cgi_fields

    def __call__(self, request, response):
        logging.debug("%s", self.title)
        if self.path_values:
            logging.debug("URL path values: %s", request.path_values)
            logging.debug("URL path named values: %s",
                          request.path_named_values.items())
        if self.environ:
            logging.debug('environ:')
            for key, value in sorted(request.environ.items()):
                logging.debug("  %s = %s", key, value)
        if self.headers:
            logging.debug('headers:')
            for key in request.headers:
                logging.debug("  %s = %s", key, request.headers[key])
        if self.cookie:
            logging.debug("cookie: %s", request.cookie)
        if self.cgi_fields:
            logging.debug("CGI fields: %s", request.cgi_fields)
        if self.user:
            logging.debug("User: %s\n" % request.user)
            logging.debug("Password: %s\n" % request.password)

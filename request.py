""" wireframe: Minimalistic Web Resource Framework built on Python WSGI.

HTTP request class.

Per Kraulis
2009-10-31
2010-01-25  added '__getitem__' and 'get' methods
2010-03-04  fixed case when no encoded data sent with request
2010-06-27  added 'is_msie' parameter
"""

import copy, cgi, Cookie, sys

from .headers import Headers


class Request(object):
    "Standard request class with input body interpreted as CGI form fields."

    HUMAN_USER_AGENT_SIGNATURES = ['mozilla', 'firefox', 'opera',
                                   'chrome', 'safari', 'msie']

    def __init__(self, environ, path_values=[], path_named_values={}):
        self.environ = environ.copy()
        self.path_values = copy.copy(path_values) # May be other than sequence
        self.path_named_values = path_named_values.copy()
        self.setup()

    def setup(self):
        "Standard setup of attributes according to the input data."
        self.setup_path()
        self.setup_headers()
        self.setup_authenticate()
        self.setup_human_user_agent()
        self.setup_cookie()
        self.setup_data()
        self.setup_http_method()

    def setup_path(self):
        "Obtain the URL path for the request."
        self.path = self.environ['PATH_INFO']

    def setup_headers(self):
        "Obtain the HTTP headers for the request."
        self.headers = Headers()
        for key in self.environ:
            if key.startswith('HTTP_'):
                self.headers[key[5:]] = str(self.environ[key])

    def setup_authenticate(self):
        "Set the 'user' and 'password' members to None."
        self.user = None
        self.password = None

    def setup_human_user_agent(self):
        "Guess whether the user agent represents a human user, i.e. a browser."
        self.human_user_agent = False
        self.human_user_agent_is_msie = False
        try:
            user_agent = self.environ['HTTP_USER_AGENT'].lower()
            for signature in self.HUMAN_USER_AGENT_SIGNATURES:
                if signature in user_agent:
                    self.human_user_agent = True
                    break
            self.human_user_agent_is_msie = 'msie' in user_agent
        except KeyError:
            pass

    def setup_cookie(self):
        "Obtain the SimpleCookie instance for the request."
        self.cookie = Cookie.SimpleCookie(self.environ.get('HTTP_COOKIE'))

    def setup_data(self):
        """Handle the input data according to content type.
        If 'application/x-www-form-urlencoded' or 'multipart/form-data',
        then interpret the input as CGI FieldStorage according to the method,
        else set the 'file' attribute to the input file handle."""
        try:                    # Strip off trailing encoding info
            self.content_type = self.environ['CONTENT_TYPE'].split(';')[0]
        except KeyError:
            self.content_type = 'application/octet-stream'
        if self.content_type in ('application/x-www-form-urlencoded',
                                 'multipart/form-data'):
            self.file = None
            request_method = self.environ['REQUEST_METHOD']
            if request_method == 'GET':
                self.cgi_fields = cgi.FieldStorage(environ=self.environ)
            else:
                # cgi.FieldStorage problem when REQUEST_METHOD is not POST
                self.environ['REQUEST_METHOD'] = 'POST'         # Workaround
                fp = self.environ['wsgi.input']
                self.cgi_fields = cgi.FieldStorage(fp=fp, environ=self.environ)
                self.environ['REQUEST_METHOD'] = request_method # Restore
        else:
            self.file = self.environ['wsgi.input']
            try:
                self.cgi_fields = cgi.FieldStorage(environ=self.environ)
            except IOError:     # sys.stdin is restricted in WSGI
                self.cgi_fields = dict()

    def setup_http_method(self):
        """Obtain the HTTP request for the request.
        If the method is POST, then it may be overloaded by
        the parameter 'http_method'."""
        self.http_method = self.environ['REQUEST_METHOD'].upper()
        if self.http_method == 'POST':
            try:
                self.http_method = self.cgi_fields['http_method'].value.upper()
            except KeyError:
                pass

    @property
    def data(self):
        "Contains the request data body, if any."
        try:
            return self._data
        except AttributeError:
            if self.file is None:
                self._data = None
            else:
                self._data = self.file.read()
                self.file = None
            return self._data

    def __getitem__(self, key):
        """Return the value of the parameter 'key'.
        If the 'key' value is an integer, then look in 'path_values'.
        Raise IndexError if the key is not present.
        Raise ValueError if 'path_values' is a string.
        Otherwise, look first in 'path_named_values', then in 'cgi_fields'.
        Raise KeyError if the key is not present there."""
        if isinstance(key, (int, long)):
            if isinstance(self.path_values, basestring):
                raise ValueError('path_values is a string; index meaningless')
            try:
                return self.path_values[key]
            except IndexError:
                raise IndexError("no such index '%s' in request data")
        else:
            try:
                return self.path_named_values[key]
            except KeyError:
                try:
                    return self.cgi_fields[key].value
                except KeyError:
                    raise KeyError("no such key '%s' in request data" % key)

    def __contains__(self, key):
        "Is the named field in 'path_named_values' or 'cgi_fields'?"
        return key in self.path_named_values or key in self.cgi_fields

    def get(self, key, default=None):
        """Return the value of the parameter 'key', or the default.
        The parameter, if it exists, must be a string value, not a file."""
        try:
            return self[key]
        except (IndexError, KeyError):
            return default

""" wireframe: Minimalistic Web Resource Framework built on Python WSGI.

Processor for producing an echo response including values from the request.

Per Kraulis
2011-01-25  split out of response.py
"""


class EchoProcessor(object):
    "Return a response containing the values of the request items."

    def __init__(self, title='Echo request',
                 path_values=True, environ=True, headers=True,
                 cookie=True, cgi_fields=True, user=True):
        self.title = title
        self.path_values = path_values
        self.environ = environ
        self.headers = headers
        self.cookie = cookie
        self.cgi_fields = cgi_fields
        self.user = user

    def __call__(self, request, response):
        response['Content-Type'] = 'text/plain'
        response.append("%s\n" % self.title)
        if self.path_values:
            response.append("URL path values: %s\n" % request.path_values)
            response.append("URL path named values: %s\n"
                            % request.path_named_values.items())
        if self.environ:
            response.append('environ:\n')
            for item in sorted(request.environ.items()):
                response.append("  %s = %s\n" % item)
        if self.headers:
            response.append('headers:\n')
            for key in request.headers:
                response.append("  %s = %s\n" % (key, request.headers[key]))
        if self.cookie:
            response.append("cookie: %s\n" % request.cookie)
        if self.cgi_fields:
            response.append("CGI fields: %s\n" % request.cgi_fields)
        if self.user:
            response.append("User: %s\n" % request.user)
            response.append("Password: %s\n" % request.password)

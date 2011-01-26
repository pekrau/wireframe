""" wireframe: Minimalistic Web Resource Framework built on Python WSGI.

Example application script.

Per Kraulis
2009-10-31
2011-01-25  reorganized
"""

from wireframe.application import Application
from wireframe.response import HTTP_CONFLICT
from wireframe.basic_authenticate import BasicAuthenticate
from wireframe.echo_processor import EchoProcessor
from wireframe.file_processor import FileProcessor
from wireframe.dispatcher import BaseDispatcher


def home(request, response):
    "An extremely simple processor."
    response['Content-Type'] = 'text/plain'
    response.append('wireframe example: home')

def conflict(request, response):
    "A processor simply returning an HTTP error status."
    raise HTTP_CONFLICT('this is an example of an HTTP error status')

def path_matcher(path):
    "Handle all other URL paths."
    return path.strip('/').split('/')

def path_echo(request, response):
    "Simply echo the path as a plain string list."
    response['Content-Type'] = 'text/plain'
    response.append("Request path values: %s" % request.path_values)


class Dispatcher(BaseDispatcher):
    "A very simple dispatcher class, showing GET and POST handling."

    template = """<html>
<head><title>wireframe example</title></head>
<body>
<h1>wireframe example</h1>
<p>%s</p>
<p>
<form method='POST'>
Input data:
<input type='text' name='data'>
<input type='submit'>
</form>
</p>
</body>
</html>"""

    def GET(self, request, response):
        response['Content-Type'] = 'text/html'
        response.append(self.template % 'GET: <i>[no data input]</i>')

    def POST(self, request, response):
        try:
            msg = "Data posted: %s" % request.cgi_fields['data'].value.strip()
        except KeyError:
            msg = 'Data posted: <b>no input data provided!</b>'
        response['Content-Type'] = 'text/html'
        response.append(self.template % msg)


application = Application()

# Simple functions as processors
application.add_map(r'^/?$', GET=home)
application.add_map(r'^/conflict$', GET=conflict)

# Processors can be chained by giving a list of them in 'add_map'
application.add_map(r'^/login$', GET=[BasicAuthenticate(realm='example'),
                                      EchoProcessor()])

# A Dispatcher class for handling all methods for a URL
application.add_class(r'^/page$', Dispatcher)

# Using a predefined processor: a callable class instance
application.add_map(r'^/file/.+$',
                    GET=FileProcessor('/home/pjk/python', '/file'))

# Example: catch all other URLs
application.add_map(path_matcher, GET=path_echo)

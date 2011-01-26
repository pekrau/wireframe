""" wireframe: Minimalistic Web Resource Framework built on Python WSGI.

Processor for server-side content negotiation.

Per Kraulis
2009-11-13
2010-06-27  fixed bug: '+' must be escaped in RE pattern for accept_types
"""

import re

from .response import HTTP_NOT_ACCEPTABLE


class ContentNegotiate(object):
    """Processor class for server-side content negotiation.
    Parse the 'Accept' HTTP header of the request and set the
    member 'content_negotiator' in the response instance to this
    instance, which provides different resolution functions."""

    def __call__(self, request, response):
        self.accept_types = parse_accept_header(request)
        response.content_negotiator = self

    def select(self, available=[]):
        """Select the best content type out of the list of available ones.
        If no 'Accept' header was provided by the request,
        then return the first entry in the content_types list.
        If no choice can be made, raise HTTP 'Not Acceptable'."""
        if self.accept_types:
            for quality, content_type_rx in self.accept_types:
                for content_type in available:
                    if content_type_rx.match(content_type):
                        return content_type
        else:
            try:
                return available[0]
            except IndexError:
                pass
            raise HTTP_NOT_ACCEPTABLE

    def is_acceptable(self, content_type):
        "Is the given content type acceptable for the request?"
        return is_content_type_acceptable(content_type, self.accept_types)

    def check_acceptable(self, content_type):
        "Raise HTTP error 'Not Acceptable' if the specified content type isn't."
        if not self.is_acceptable(content_type):
            raise HTTP_NOT_ACCEPTABLE


def parse_accept_header(request):
    """Parse the 'Accept' header for mimetype and quality values.
    Return the result as a list sorted in descending order
    containing tuples of (quality, content_type_re), where
    'content_type_re' is a compiled regexp translation of the given
    content type specification, handling '*' and '.' properly."""
    result = []
    for item in request.headers.get('Accept', '').split(','):
        item = item.strip()
        if not item: continue
        try:
            content_type, param = item.split(';')
        except ValueError:
            content_type = item
            quality = 1.0
        else:
            param = param.replace(' ', '')
            if param.startswith('q='):
                try:
                    quality = float(param[2:])
                except ValueError:
                    quality = 1.0
            else:
                quality = 1.0
        result.append(get_accept_item(quality, content_type))
    result.sort(reverse=True)
    return result

def get_accept_item(quality, content_type):
    "Return a tuple (quality, content_type_re) for use in accept list."
    content_type = content_type.replace('.', r'\.')
    content_type = content_type.replace('+', r'\+')
    content_type = content_type.replace('*', r'\S*?')
    content_type = r'^' + content_type + r'$'
    return (quality, re.compile(content_type))

def is_content_type_acceptable(content_type, accept_types):
    """Given the list previously generated by 'parse_accept_header',
    is the content type (MIME type) specified by 'mime_type acceptable?"""
    for quality, content_type_rx in accept_types:
        if content_type_rx.match(content_type):
            return True
    return False

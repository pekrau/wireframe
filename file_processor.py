""" wireframe: Minimalistic Web Resource Framework built on Python WSGI.

Processor to return a file from a directory tree given by its root.
The file path is computed by appending the URL minus a specified
prefix to the specified root.

The content type is set to the mimetype guessed from the filename extension.

Per Kraulis
2009-11-14
"""

import os.path, mimetypes, logging

from .response import HTTP_INTERNAL_SERVER_ERROR, HTTP_FORBIDDEN, HTTP_NOT_FOUND


class FileProcessor(object):
    """Processor to return a file from a directory given by its root.
    The file path is computed by appending the URL minus a specified
    prefix to the specified root."""

    def __init__(self, root, prefix):
        self.root = root
        self.prefix = prefix

    def __call__(self, request, response):
        relpath = request.path
        if not relpath.startswith(self.prefix):
            raise HTTP_INTERNAL_SERVER_ERROR('invalid file path prefix')
        relpath = relpath[len(self.prefix):].lstrip('/') # Must be relative
        path = os.path.normpath(os.path.join(self.root, relpath))
        # Check for attempt to go outside the allowed directory.
        if not path.startswith(self.root):
            logging.error("Outside allowed directory: root='%s', path='%s'",
                          self.root, path)
            raise HTTP_FORBIDDEN()
        try:
            mimetype = self.get_mimetype(path)
            if self.is_mimetype_text(mimetype):
                mode = 'rt'
            else:
                mode = 'r'
            response['Content-Type'] = mimetype
            response.append(open(path, mode).read())
        except IOError:
            raise HTTP_NOT_FOUND()

    def get_mimetype(self, path, strict=False):
        """Return the mimetype for the given file path.
        By default uses 'guess_type' from the standard module 'mimetypes'.
        To be redefined when required."""
        mimetype = mimetypes.guess_type(path, strict=strict)[0]
        return mimetype or 'application/octet-stream'

    def is_mimetype_text(self, mimetype):
        """Does the given mimetype denote text content?
        This is used for opening the file in the correct mode.
        By default checks for the major mimetype 'text'.
        To be redefined when required."""
        return mimetype.startswith('text/')

""" wireframe: Minimalistic Web Resource Framework built on Python WSGI.

HTTP headers class.

Per Kraulis
2009-11-23  split out of response.py
"""

import Cookie


class Headers(object):
    """Container for HTTP headers, behaving as a dictionary with keys
    converted to lower case and underscores to dashes.
    An attribute 'cookie', which is a Cookie.SimpleCookie instance
    is available for cookie output.
    Setting an item to a value evaluating to False deletes the item."""

    def __init__(self):
        self._items = dict()
        self.cookie = Cookie.SimpleCookie()

    def __str__(self):
        return str(self.items)

    def __getitem__(self, key):
        return self._items[self.canonical_key(key)]

    def __setitem__(self, key, value):
        if value:
            self._items[self.canonical_key(key)] = str(value)
        else:
            try:
                del self[key]
            except KeyError:
                pass

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def __delitem__(self, key):
        del self._items[self.canonical_key(key)]

    def __iter__(self):
        return iter(self._items)

    @staticmethod
    def canonical_key(key):
        return key.lower().replace('_', '-')

    def update(self, other):
        "Copy over the values from the 'other' Headers instance to this."
        for key in other:
            self[key] = other[key]
        for key, morsel in other.cookie.items():
            self.cookie[key] = morsel.copy()

    @property
    def items(self):
        result = self._items.items()
        for key, morsel in self.cookie.items():
            value = str(morsel).split(':')[1].strip()
            result.append(('Set-Cookie', value))
        return result

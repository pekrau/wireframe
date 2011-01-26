""" wireframe: Minimalistic Web Resource Framework built on Python WSGI.

MySQL processor and response classes.

Per Kraulis
2009-10-31
2009-11-17  fixed 'close'
"""

import MySQLdb


class MysqlConnect(object):
    """Processor to create and open a MySQL connection stored in
    the response instance as the attribute 'cnx'. The user and password
    is provided on instance creation.
    The MySQL connection is closed when the response instance
    method 'close' is called."""

    def __init__(self, user=None, password=None,
                 db=None, port=3306, host='localhost'):
        self.user = user
        self.password = password
        self.db = db
        self.port = port
        self.host = host

    def __call__(self, request, response):
        """Open a connection to a MySQL server using the parameters
        provided at creation of this instance."""
        response.cnx = MySQLdb.connect(user=self.user,
                                       passwd=self.password,
                                       db=self.db,
                                       port=self.port,
                                       host=self.host)
        response.cleanup.append(response.cnx.close)


class MysqlAuthorize(object):
    """Processor to create and open a MySQL connection stored in
    the response instance as the attribute 'cnx'.
    The user name and password are obtained from the attributes 'user'
    and 'password' in the input Request instance, or set to blank if
    non-existent. These are the members set by BasicAuthenticate.
    The MySQL connection is closed when the response instance
    method 'close' is called."""

    def __init__(self, db=None, port=3306, host='localhost'):
        self.db = db
        self.port = port
        self.host = host

    def __call__(self, request, response):
        """Open a connection to a MySQL server using the parameters
        provided in the input response instance."""
        try:
            user = request.user or ''
        except AttributeError:
            user = ''
        try:
            password = request.password or ''
        except AttributeError:
            password = ''
        response.cnx = MySQLdb.connect(user=user,
                                       passwd=password,
                                       db=self.db,
                                       port=self.port,
                                       host=self.host)
        response.cleanup.append(response.cnx.close)

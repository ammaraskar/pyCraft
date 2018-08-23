from http import HTTPStatus
import socketserver
import http.server
import logging
import re

from builtins import super


class FakeAuthServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    """
        An HTTP server that behaves like Mojang's auth- and session-servers,
        implementing the Yggdrasil protocol, suitable for automatic testing.

        By default, the server listens on 'localhost' on an arbitrary port.
        The 'auth_url' and 'session_url' properties give the base URLs of the
        respective services.
    """

    auth_path = '/auth'
    session_path = '/session'

    def __init__(self, host='localhost', port=0):
        super().__init__((host, port), FakeAuthHandler)

    def serve_forever(self, *args, **kwds):
        self.log_message('Listening on <%s>.', self.base_url)
        super().serve_forever(*args, **kwds)
        self.log_message('Server closed.')

    def log_message(self, format_string, *args):
        logging.debug(('[AUTH] ' + format_string) % args)

    @property
    def base_url(self):
        return('http://%s:%d' % (self.server_name, self.server_port))

    @property
    def auth_url(self):
        return(self.base_url + self.auth_path)

    @property
    def session_url(self):
        return(self.base_url + self.session_path)


class FakeAuthHandler(http.server.BaseHTTPRequestHandler):
    """
       Represents the individual requests being handled by a 'FakeAuthServer'.
    """
    def handle_auth(self, method, path):
        # Possibly handle an auth-server request. Return True if handled.
        return False

    def handle_session(self, method, path):
        # Possibly handle a session-server request. Return True if handled.
        return False

    def do_method(self, method):
        # Handle a GET or POST request, given the method string.
        head, tail = re.match(r'(/?[^/]*)(.*)', self.path).groups()
        for path, handler in ((self.server.auth_path, self.handle_auth),
                              (self.server.session_path, self.handle_session)):
            if head == path and handler(method, tail):
                return
        self.send_error(HTTPStatus.NOT_FOUND)

    def do_GET(self):
        self.do_method('GET')

    def do_POST(self):
        self.do_method('POST')

    def log_message(self, *args, **kwds):
        self.server.log_message(*args, **kwds)

from minecraft import SUPPORTED_MINECRAFT_VERSIONS
from minecraft import SUPPORTED_PROTOCOL_VERSIONS
from minecraft.networking.packets import clientbound, serverbound
from minecraft.networking.connection import Connection, IgnorePacket
from minecraft.exceptions import (
    VersionMismatch, LoginDisconnect, InvalidState
)
from minecraft.compat import unicode

from . import fake_server

import sys
import re
import io


class ConnectTest(fake_server._FakeServerTest):
    def test_connect(self):
        self._test_connect()

    class client_handler_type(fake_server.FakeClientHandler):
        def handle_play_start(self):
            super(ConnectTest.client_handler_type, self).handle_play_start()
            self.write_packet(clientbound.play.KeepAlivePacket(
                keep_alive_id=1223334444))

        def handle_play_packet(self, packet):
            super(ConnectTest.client_handler_type, self) \
                .handle_play_packet(packet)
            if isinstance(packet, serverbound.play.KeepAlivePacket):
                assert packet.keep_alive_id == 1223334444
                raise fake_server.FakeServerDisconnect


class PingTest(ConnectTest):
    def _start_client(self, client):
        def handle_ping(latency_ms):
            assert 0 <= latency_ms < 60000
            raise fake_server.FakeServerTestSuccess
        client.status(handle_status=False, handle_ping=handle_ping)


class StatusTest(ConnectTest):
    def _start_client(self, client):
        def handle_status(status_dict):
            assert status_dict['description'] == {'text': 'FakeServer'}
            raise fake_server.FakeServerTestSuccess
        client.status(handle_status=handle_status, handle_ping=False)


class DefaultStatusTest(ConnectTest):
    def setUp(self):
        class FakeStdOut(io.BytesIO):
            def write(self, data):
                if isinstance(data, unicode):
                    data = data.encode('utf8')
                super(FakeStdOut, self).write(data)
        sys.stdout, self.old_stdout = FakeStdOut(), sys.stdout

    def tearDown(self):
        sys.stdout, self.old_stdout = self.old_stdout, None

    def _start_client(self, client):
        def handle_exit():
            output = sys.stdout.getvalue()
            assert re.match(b'{.*}\\nPing: \\d+ ms\\n$', output), \
                'Invalid stdout contents: %r.' % output
            raise fake_server.FakeServerTestSuccess
        client.handle_exit = handle_exit

        client.status(handle_status=None, handle_ping=None)


class ConnectCompressionLowTest(ConnectTest):
    compression_threshold = 0


class ConnectCompressionHighTest(ConnectTest):
    compression_threshold = 256


class AllowedVersionsTest(fake_server._FakeServerTest):
    versions = sorted(SUPPORTED_MINECRAFT_VERSIONS.items(), key=lambda p: p[1])
    versions = dict((versions[0], versions[len(versions)//2], versions[-1]))

    client_handler_type = ConnectTest.client_handler_type

    def test_with_version_names(self):
        for version, proto in AllowedVersionsTest.versions.items():
            client_versions = {
                v for (v, p) in SUPPORTED_MINECRAFT_VERSIONS.items()
                if p <= proto}
            self._test_connect(
                server_version=version, client_versions=client_versions)

    def test_with_protocol_numbers(self):
        for version, proto in AllowedVersionsTest.versions.items():
            client_versions = {
                p for (v, p) in SUPPORTED_MINECRAFT_VERSIONS.items()
                if p <= proto}
            self._test_connect(
                server_version=version, client_versions=client_versions)


class LoginDisconnectTest(fake_server._FakeServerTest):
    def test_login_disconnect(self):
        with self.assertRaisesRegexp(LoginDisconnect, r'You are banned'):
            self._test_connect()

    class client_handler_type(fake_server.FakeClientHandler):
        def handle_login(self, login_start_packet):
            raise fake_server.FakeServerDisconnect('You are banned.')


class ConnectTwiceTest(fake_server._FakeServerTest):
    def test_connect(self):
        with self.assertRaisesRegexp(InvalidState, 'existing connection'):
            self._test_connect()

    class client_handler_type(fake_server.FakeClientHandler):
        def handle_play_start(self):
            super(ConnectTwiceTest.client_handler_type, self) \
                .handle_play_start()
            raise fake_server.FakeServerDisconnect('Test complete.')

    def _start_client(self, client):
        client.connect()
        client.connect()


class ConnectStatusTest(ConnectTwiceTest):
    def _start_client(self, client):
        client.connect()
        client.status()


class EarlyPacketListenerTest(ConnectTest):
    """ Early packet listeners should be called before ordinary ones, even when
        the early packet listener is registered afterwards.
    """
    def _start_client(self, client):
        def handle_join(packet):
            assert early_handle_join.called, \
                   'Ordinary listener called before early listener.'
            handle_join.called = True
        handle_join.called = False
        client.register_packet_listener(
            handle_join, clientbound.play.JoinGamePacket)

        def early_handle_join(packet):
            early_handle_join.called = True
        client.register_packet_listener(
            early_handle_join, clientbound.play.JoinGamePacket, early=True)
        early_handle_join.called = False

        def handle_disconnect(packet):
            assert early_handle_join.called, 'Early listener not called.'
            assert handle_join.called, 'Ordinary listener not called.'
            raise fake_server.FakeServerTestSuccess
        client.register_packet_listener(
            handle_disconnect, clientbound.play.DisconnectPacket)

        client.connect()


class IgnorePacketTest(ConnectTest):
    """ Raising 'minecraft.networking.connection.IgnorePacket' from within a
        packet listener should prevent any subsequent packet listeners from
        being called, and, if the listener is early, should prevent the default
        behaviour from being triggered.
    """

    def _start_client(self, client):
        keep_alive_ids_incoming = []
        keep_alive_ids_outgoing = []

        def handle_keep_alive_1(packet):
            keep_alive_ids_incoming.append(packet.keep_alive_id)
            if packet.keep_alive_id == 1:
                raise IgnorePacket
        client.register_packet_listener(
            handle_keep_alive_1, clientbound.play.KeepAlivePacket, early=True)

        def handle_keep_alive_2(packet):
            keep_alive_ids_incoming.append(packet.keep_alive_id)
            assert packet.keep_alive_id > 1
            if packet.keep_alive_id == 2:
                raise IgnorePacket
        client.register_packet_listener(
            handle_keep_alive_2, clientbound.play.KeepAlivePacket)

        def handle_keep_alive_3(packet):
            keep_alive_ids_incoming.append(packet.keep_alive_id)
            assert packet.keep_alive_id == 3
        client.register_packet_listener(
            handle_keep_alive_3, clientbound.play.KeepAlivePacket)

        def handle_outgoing_keep_alive_2(packet):
            keep_alive_ids_outgoing.append(packet.keep_alive_id)
            assert 2 <= packet.keep_alive_id <= 3
            if packet.keep_alive_id == 2:
                raise IgnorePacket
        client.register_packet_listener(
            handle_outgoing_keep_alive_2, serverbound.play.KeepAlivePacket,
            outgoing=True, early=True)

        def handle_outgoing_keep_alive_3(packet):
            keep_alive_ids_outgoing.append(packet.keep_alive_id)
            assert packet.keep_alive_id == 3
            raise IgnorePacket
        client.register_packet_listener(
            handle_outgoing_keep_alive_3, serverbound.play.KeepAlivePacket,
            outgoing=True)

        def handle_outgoing_keep_alive_none(packet):
            keep_alive_ids_outgoing.append(packet.keep_alive_id)
            assert False
        client.register_packet_listener(
            handle_outgoing_keep_alive_none, serverbound.play.KeepAlivePacket,
            outgoing=True)

        def handle_disconnect(packet):
            assert keep_alive_ids_incoming == [1, 2, 2, 3, 3, 3], \
                'Incoming keep-alive IDs %r != %r' % \
                (keep_alive_ids_incoming, [1, 2, 2, 3, 3, 3])
            assert keep_alive_ids_outgoing == [2, 3, 3], \
                'Outgoing keep-alive IDs %r != %r' % \
                (keep_alive_ids_incoming, [2, 3, 3])
        client.register_packet_listener(
            handle_disconnect, clientbound.play.DisconnectPacket)

        client.connect()

    class client_handler_type(fake_server.FakeClientHandler):
        __slots__ = '_keep_alive_ids_returned'

        def __init__(self, *args, **kwds):
            super(IgnorePacketTest.client_handler_type, self).__init__(
                *args, **kwds)
            self._keep_alive_ids_returned = []

        def handle_play_start(self):
            super(IgnorePacketTest.client_handler_type, self)\
                .handle_play_start()
            self.write_packet(clientbound.play.KeepAlivePacket(
                keep_alive_id=1))
            self.write_packet(clientbound.play.KeepAlivePacket(
                keep_alive_id=2))
            self.write_packet(clientbound.play.KeepAlivePacket(
                keep_alive_id=3))
            self.handle_play_server_disconnect('Test complete.')

        def handle_play_packet(self, packet):
            super(IgnorePacketTest.client_handler_type, self) \
                .handle_play_packet(packet)
            if isinstance(packet, serverbound.play.KeepAlivePacket):
                self._keep_alive_ids_returned.append(packet.keep_alive_id)

        def handle_play_client_disconnect(self):
            assert self._keep_alive_ids_returned == [3], \
                   'Returned keep-alive IDs %r != %r' % \
                   (self._keep_alive_ids_returned, [3])
            raise fake_server.FakeServerTestSuccess


class HandleExceptionTest(ConnectTest):
    ignore_extra_exceptions = True

    def _start_client(self, client):
        message = 'Min skoldpadda ar inte snabb, men den ar en skoldpadda.'

        def handle_login_success(_packet):
            raise Exception(message)
        client.register_packet_listener(
            handle_login_success, clientbound.login.LoginSuccessPacket)

        def handle_exception(exc, exc_info):
            assert isinstance(exc, Exception) and exc.args == (message,)
            raise fake_server.FakeServerTestSuccess
        client.handle_exception = handle_exception

        client.connect()


class VersionNegotiationEdgeCases(fake_server._FakeServerTest):
    lowest_version = min(SUPPORTED_PROTOCOL_VERSIONS)
    highest_version = max(SUPPORTED_PROTOCOL_VERSIONS)
    impossible_version = highest_version + 1

    def test_client_protocol_unsupported(self):
        self._test_client_protocol(version=self.impossible_version)

    def test_client_protocol_unknown(self):
        self._test_client_protocol(version='surprise me!')

    def test_client_protocol_invalid(self):
        self._test_client_protocol(version=object())

    def _test_client_protocol(self, version):
        with self.assertRaisesRegexp(ValueError, 'Unsupported version'):
            self._test_connect(client_versions={version})

    def test_server_protocol_unsupported(self, client_versions=None):
        with self.assertRaisesRegexp(VersionMismatch, 'not supported'):
            self._test_connect(client_versions=client_versions,
                               server_version=self.impossible_version)

    def test_server_protocol_unsupported_direct(self):
        self.test_server_protocol_unsupported({self.highest_version})

    def test_server_protocol_disallowed(self, client_versions=None):
        if client_versions is None:
            client_versions = set(SUPPORTED_PROTOCOL_VERSIONS) \
                              - {self.highest_version}
        with self.assertRaisesRegexp(VersionMismatch, 'not allowed'):
            self._test_connect(client_versions={self.lowest_version},
                               server_version=self.highest_version)

    def test_server_protocol_disallowed_direct(self):
        self.test_server_protocol_disallowed({self.lowest_version})

    def test_default_protocol_version(self, status_response=None):
        if status_response is None:
            status_response = '{"description": {"text": "FakeServer"}}'

        class ClientHandler(fake_server.FakeClientHandler):
            def _run_status(self):
                packet = clientbound.status.ResponsePacket()
                packet.json_response = status_response
                self.write_packet(packet)

            def handle_play_start(self):
                super(ClientHandler, self).handle_play_start()
                raise fake_server.FakeServerDisconnect('Test complete.')

        def make_connection(*args, **kwds):
            kwds['initial_version'] = self.lowest_version
            return Connection(*args, **kwds)

        self._test_connect(server_version=self.lowest_version,
                           client_handler_type=ClientHandler,
                           connection_type=make_connection)

    def test_default_protocol_version_empty(self):
        with self.assertRaisesRegexp(IOError, 'Invalid server status'):
            self.test_default_protocol_version(status_response='{}')

    def test_default_protocol_version_eof(self):
        class ClientHandler(fake_server.FakeClientHandler):
            def handle_status(self, request_packet):
                raise fake_server.FakeServerDisconnect(
                      'Refusing to handle status request, for test purposes.')

            def handle_play_start(self):
                super(ClientHandler, self).handle_play_start()
                raise fake_server.FakeServerDisconnect('Test complete.')

        def make_connection(*args, **kwds):
            kwds['initial_version'] = self.lowest_version
            return Connection(*args, **kwds)

        self._test_connect(server_version=self.lowest_version,
                           client_handler_type=ClientHandler,
                           connection_type=make_connection)

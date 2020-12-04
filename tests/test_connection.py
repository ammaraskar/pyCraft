from minecraft import (
    SUPPORTED_MINECRAFT_VERSIONS, SUPPORTED_PROTOCOL_VERSIONS,
    PROTOCOL_VERSION_INDICES,
)
from minecraft.networking.packets import clientbound, serverbound
from minecraft.networking.connection import Connection
from minecraft.exceptions import (
    VersionMismatch, LoginDisconnect, InvalidState, IgnorePacket
)

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


class ReconnectTest(ConnectTest):
    phase = 0

    def _start_client(self, client):
        def handle_login_disconnect(packet):
            if 'Please reconnect' in packet.json_data:
                # Override the default behaviour of raising a fatal exception.
                client.disconnect()
                client.connect()
                raise IgnorePacket
        client.register_packet_listener(
            handle_login_disconnect, clientbound.login.DisconnectPacket,
            early=True)

        def handle_play_disconnect(packet):
            if 'Please reconnect' in packet.json_data:
                client.connect()
            elif 'Test successful' in packet.json_data:
                raise fake_server.FakeServerTestSuccess
        client.register_packet_listener(
            handle_play_disconnect, clientbound.play.DisconnectPacket)

        client.connect()

    class client_handler_type(fake_server.FakeClientHandler):
        def handle_login(self, packet):
            if self.server.test_case.phase == 0:
                self.server.test_case.phase = 1
                raise fake_server.FakeServerDisconnect('Please reconnect (0).')
            super(ReconnectTest.client_handler_type, self).handle_login(packet)

        def handle_play_start(self):
            if self.server.test_case.phase == 1:
                self.server.test_case.phase = 2
                raise fake_server.FakeServerDisconnect('Please reconnect (1).')
            else:
                assert self.server.test_case.phase == 2
                raise fake_server.FakeServerDisconnect('Test successful (2).')


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
                if isinstance(data, str):
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
    versions = list(SUPPORTED_MINECRAFT_VERSIONS.items())
    test_indices = (0, len(versions) // 2, len(versions) - 1)

    client_handler_type = ConnectTest.client_handler_type

    def test_with_version_names(self):
        for index in self.test_indices:
            self._test_connect(
                server_version=self.versions[index][0],
                client_versions={v[0] for v in self.versions[:index+1]})

    def test_with_protocol_numbers(self):
        for index in self.test_indices:
            self._test_connect(
                server_version=self.versions[index][0],
                client_versions={v[1] for v in self.versions[:index+1]})


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


class LoginPluginTest(fake_server._FakeServerTest):
    class client_handler_type(fake_server.FakeClientHandler):
        def handle_login(self, login_start_packet):
            request = clientbound.login.PluginRequestPacket(
                message_id=1, channel='pyCraft:tests/fail', data=b'ignored')
            self.write_packet(request)
            response = self.read_packet()
            assert isinstance(response, serverbound.login.PluginResponsePacket)
            assert response.message_id == request.message_id
            assert response.successful is False
            assert response.data is None

            request = clientbound.login.PluginRequestPacket(
                message_id=2, channel='pyCraft:tests/echo', data=b'hello')
            self.write_packet(request)
            response = self.read_packet()
            assert isinstance(response, serverbound.login.PluginResponsePacket)
            assert response.message_id == request.message_id
            assert response.successful is True
            assert response.data == request.data

            super(LoginPluginTest.client_handler_type, self) \
                .handle_login(login_start_packet)

        def handle_play_start(self):
            super(LoginPluginTest.client_handler_type, self) \
                .handle_play_start()
            raise fake_server.FakeServerDisconnect

    def _start_client(self, client):
        def handle_plugin_request(packet):
            if packet.channel == 'pyCraft:tests/echo':
                client.write_packet(serverbound.login.PluginResponsePacket(
                    message_id=packet.message_id, data=packet.data))
                raise IgnorePacket
        client.register_packet_listener(
            handle_plugin_request, clientbound.login.PluginRequestPacket,
            early=True)

        super(LoginPluginTest, self)._start_client(client)

    def test_login_plugin_messages(self):
        self._test_connect()


class EarlyPacketListenerTest(ConnectTest):
    """ Early packet listeners should be called before ordinary ones, even when
        the early packet listener is registered afterwards.
    """
    def _start_client(self, client):
        @client.listener(clientbound.play.JoinGamePacket)
        def handle_join(packet):
            assert early_handle_join.called, \
                   'Ordinary listener called before early listener.'
            handle_join.called = True
        handle_join.called = False

        @client.listener(clientbound.play.JoinGamePacket, early=True)
        def early_handle_join(packet):
            early_handle_join.called = True
        early_handle_join.called = False

        @client.listener(clientbound.play.DisconnectPacket)
        def handle_disconnect(packet):
            assert early_handle_join.called, 'Early listener not called.'
            assert handle_join.called, 'Ordinary listener not called.'
            raise fake_server.FakeServerTestSuccess

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

        @client.listener(clientbound.login.LoginSuccessPacket)
        def handle_login_success(_packet):
            raise Exception(message)

        @client.exception_handler(early=True)
        def handle_exception(exc, _exc_info):
            assert isinstance(exc, Exception) and exc.args == (message,)
            raise fake_server.FakeServerTestSuccess

        client.connect()


class ExceptionReconnectTest(ConnectTest):
    class CustomException(Exception):
        pass

    def setUp(self):
        self.phase = 0

    def _start_client(self, client):
        @client.listener(clientbound.play.JoinGamePacket)
        def handle_join_game(packet):
            if self.phase == 0:
                self.phase += 1
                raise self.CustomException
            else:
                raise fake_server.FakeServerTestSuccess

        @client.exception_handler(self.CustomException, early=True)
        def handle_custom_exception(exc, exc_info):
            client.disconnect(immediate=True)
            client.connect()

        client.connect()

    class client_handler_type(ConnectTest.client_handler_type):
        def handle_abnormal_disconnect(self, exc):
            return True


class VersionNegotiationEdgeCases(fake_server._FakeServerTest):
    earliest_version = SUPPORTED_PROTOCOL_VERSIONS[0]
    latest_version = SUPPORTED_PROTOCOL_VERSIONS[-1]

    fake_version = max(PROTOCOL_VERSION_INDICES.keys()) + 1
    fake_version_index = max(PROTOCOL_VERSION_INDICES.values()) + 1

    def setUp(self):
        PROTOCOL_VERSION_INDICES[self.fake_version] = self.fake_version_index
        super(VersionNegotiationEdgeCases, self).setUp()

    def tearDown(self):
        super(VersionNegotiationEdgeCases, self).tearDown()
        del PROTOCOL_VERSION_INDICES[self.fake_version]

    def test_client_protocol_unsupported(self):
        self._test_client_protocol(version=self.fake_version)

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
                               server_version=self.fake_version)

    def test_server_protocol_unsupported_direct(self):
        self.test_server_protocol_unsupported({self.latest_version})

    def test_server_protocol_disallowed(self, client_versions=None):
        if client_versions is None:
            client_versions = set(SUPPORTED_PROTOCOL_VERSIONS) \
                              - {self.latest_version}
        with self.assertRaisesRegexp(VersionMismatch, 'not allowed'):
            self._test_connect(client_versions={self.earliest_version},
                               server_version=self.latest_version)

    def test_server_protocol_disallowed_direct(self):
        self.test_server_protocol_disallowed({self.earliest_version})

    def test_default_protocol_version(self, status_response=None):
        if status_response is None:
            status_response = '{"description": {"text": "FakeServer"}}'

        class ClientHandler(fake_server.FakeClientHandler):
            def handle_status(self, request_packet):
                packet = clientbound.status.ResponsePacket()
                packet.json_response = status_response
                self.write_packet(packet)

            def handle_play_start(self):
                super(ClientHandler, self).handle_play_start()
                raise fake_server.FakeServerDisconnect('Test complete.')

        def make_connection(*args, **kwds):
            kwds['initial_version'] = self.earliest_version
            return Connection(*args, **kwds)

        self._test_connect(server_version=self.earliest_version,
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
            kwds['initial_version'] = self.earliest_version
            return Connection(*args, **kwds)

        self._test_connect(server_version=self.earliest_version,
                           client_handler_type=ClientHandler,
                           connection_type=make_connection)

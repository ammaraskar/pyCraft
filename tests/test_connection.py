from minecraft import SUPPORTED_MINECRAFT_VERSIONS
from minecraft.networking.packets import clientbound, serverbound
from minecraft.networking.connection import IgnorePacket

from . import fake_server


class ConnectTest(fake_server._FakeServerTest):
    def test_connect(self):
        self._test_connect()

    class client_handler_type(fake_server.FakeClientHandler):
        def handle_play_start(self):
            super(ConnectTest.client_handler_type, self).handle_play_start()
            raise fake_server.FakeServerDisconnect


class PingTest(ConnectTest):
    def _start_client(self, client):
        def handle_ping(latency_ms):
            assert 0 <= latency_ms < 60000
            raise fake_server.FakeServerTestSuccess
        client.status(handle_status=False, handle_ping=handle_ping)


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
            self.write_packet(clientbound.play.DisconnectPacket(
                json_data='{"text":"Test complete."}'))

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

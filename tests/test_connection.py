from __future__ import print_function

from minecraft import SUPPORTED_MINECRAFT_VERSIONS
from minecraft.networking import connection
from minecraft.networking import types
from minecraft.networking import packets

from future.utils import raise_

import unittest
import threading
import logging
import socket
import json
import sys

VERSIONS = sorted(SUPPORTED_MINECRAFT_VERSIONS.items(), key=lambda i: i[1])
THREAD_TIMEOUT_S = 5


class _ConnectTest(unittest.TestCase):
    def _test_connect(self, client_version=None, server_version=None):
        server = FakeServer(minecraft_version=server_version)
        addr, port = server.listen_socket.getsockname()

        cond = threading.Condition()

        def handle_client_exception(exc, exc_info):
            with cond:
                cond.exc_info = exc_info
                cond.notify_all()

        def client_write(packet, *args, **kwds):
            def packet_write(*args, **kwds):
                logging.debug('[C-> ] %s' % packet)
                return real_packet_write(*args, **kwds)
            real_packet_write = packet.write
            packet.write = packet_write
            return real_client_write(packet, *args, **kwds)

        def client_react(packet, *args, **kwds):
            logging.debug('[ ->C] %s' % packet)
            return real_client_react(packet, *args, **kwds)

        client = connection.Connection(
            addr, port, username='User', initial_version=client_version,
            handle_exception=handle_client_exception)
        real_client_react = client._react
        real_client_write = client.write_packet
        client.write_packet = client_write
        client._react = client_react

        try:
            with cond:
                server_thread = threading.Thread(
                    name='_ConnectTest server',
                    target=self._test_connect_server,
                    args=(server, cond))
                server_thread.daemon = True
                server_thread.start()

                self._test_connect_client(client, cond)

                cond.exc_info = Ellipsis
                cond.wait(THREAD_TIMEOUT_S)
                if cond.exc_info is Ellipsis:
                    self.fail('Timed out.')
                elif cond.exc_info is not None:
                    raise_(*cond.exc_info)
        finally:
            # Wait for all threads to exit.
            for thread in server_thread, client.networking_thread:
                if thread is not None and thread.is_alive():
                    thread.join(THREAD_TIMEOUT_S)
                if thread is not None and thread.is_alive():
                    if cond.exc_info is None:
                        self.fail('Thread "%s" timed out.' % thread.name)
                    else:
                        # Keep the earlier exception, if there is one.
                        break

    def _test_connect_client(self, client, cond):
        client.connect()

    def _test_connect_server(self, server, cond):
        try:
            server.run()
            exc_info = None
        except:
            exc_info = sys.exc_info()
        with cond:
            cond.exc_info = exc_info
            cond.notify_all()


class ConnectOldToOldTest(_ConnectTest):
    def runTest(self):
        self._test_connect(VERSIONS[0][1], VERSIONS[0][0])


class ConnectOldToNewTest(_ConnectTest):
    def runTest(self):
        self._test_connect(VERSIONS[0][1], VERSIONS[-1][0])


class ConnectNewToOldTest(_ConnectTest):
    def runTest(self):
        self._test_connect(VERSIONS[-1][1], VERSIONS[0][0])


class ConnectNewToNewTest(_ConnectTest):
    def runTest(self):
        self._test_connect(VERSIONS[-1][1], VERSIONS[-1][0])


class PingTest(_ConnectTest):
    def runTest(self):
        self._test_connect()

    def _test_connect_client(self, client, cond):
        def handle_ping(latency_ms):
            assert 0 <= latency_ms < 60000
            with cond:
                cond.exc_info = None
                cond.notify_all()
        client.status(handle_status=False, handle_ping=handle_ping)

    def _test_connect_server(self, server, cond):
        try:
            server.continue_after_status = False
            server.run()
        except:
            with cond:
                cond.exc_info = sys.exc_info()
                cond.notify_all()


class FakeServer(threading.Thread):
    __slots__ = 'context', 'minecraft_version', 'listen_socket', \
                'packets_login', 'packets_playing', 'packets_status', \
                'packets',

    def __init__(self, minecraft_version=None, continue_after_status=True):
        if minecraft_version is None:
            minecraft_version = VERSIONS[-1][0]
        self.minecraft_version = minecraft_version
        self.continue_after_status = continue_after_status
        protocol_version = SUPPORTED_MINECRAFT_VERSIONS[minecraft_version]
        self.context = connection.ConnectionContext(
            protocol_version=protocol_version)

        self.packets_handshake = {
            p.get_id(self.context): p for p in
            packets.state_handshake_serverbound(self.context)}

        self.packets_login = {
            p.get_id(self.context): p for p in
            packets.state_login_serverbound(self.context)}

        self.packets_playing = {
            p.get_id(self.context): p for p in
            packets.state_playing_serverbound(self.context)}

        self.packets_status = {
            p.get_id(self.context): p for p in
            packets.state_status_serverbound(self.context)}

        self.listen_socket = socket.socket()
        self.listen_socket.bind(('0.0.0.0', 0))
        self.listen_socket.listen(0)

        super(FakeServer, self).__init__()

    def run(self):
        try:
            self.run_accept()
        finally:
            self.listen_socket.close()

    def run_accept(self):
        running = True
        while running:
            client_socket, addr = self.listen_socket.accept()
            logging.debug('[ ++ ] Client %s connected to server.' % (addr,))
            client_file = client_socket.makefile('rb', 0)
            try:
                running = self.run_handshake(client_socket, client_file)
            except:
                raise
            else:
                client_socket.shutdown(socket.SHUT_RDWR)
                logging.debug('[ -- ] Client %s disconnected.' % (addr,))
            finally:
                client_socket.close()
                client_file.close()

    def run_handshake(self, client_socket, client_file):
        self.packets = self.packets_handshake
        packet = self.read_packet_filtered(client_file)
        assert isinstance(packet, packets.HandShakePacket)
        if packet.next_state == 1:
            return self.run_handshake_status(
                packet, client_socket, client_file)
        elif packet.next_state == 2:
            return self.run_handshake_play(
                packet, client_socket, client_file)
        else:
            raise AssertionError('Unknown state: %s' % packet.next_state)

    def run_handshake_status(self, packet, client_socket, client_file):
        self.run_status(client_socket, client_file)
        return self.continue_after_status

    def run_handshake_play(self, packet, client_socket, client_file):
        if packet.protocol_version == self.context.protocol_version:
            self.run_login(client_socket, client_file)
        else:
            if packet.protocol_version < self.context.protocol_version:
                msg = 'Outdated client! Please use %s' \
                      % self.minecraft_version
            else:
                msg = "Outdated server! I'm still on %s" \
                      % self.minecraft_version
            packet = packets.DisconnectPacket(
                self.context, json_data=json.dumps({'text': msg}))
            self.write_packet(packet, client_socket)
            return True

    def run_login(self, client_socket, client_file):
        self.packets = self.packets_login
        packet = self.read_packet_filtered(client_file)
        assert isinstance(packet, packets.LoginStartPacket)

        packet = packets.LoginSuccessPacket(
            self.context, UUID='{fake uuid}', Username=packet.name)
        self.write_packet(packet, client_socket)
        self.run_playing(client_socket, client_file)

    def run_playing(self, client_socket, client_file):
        self.packets = self.packets_playing

        packet = packets.JoinGamePacket(
            self.context, entity_id=0, game_mode=0, dimension=0, difficulty=2,
            max_players=1, level_type='default', reduced_debug_info=False)
        self.write_packet(packet, client_socket)

        keep_alive_id = 1076048782
        packet = packets.KeepAlivePacketClientbound(
            self.context, keep_alive_id=keep_alive_id)
        self.write_packet(packet, client_socket)

        packet = self.read_packet_filtered(client_file)
        assert isinstance(packet, packets.KeepAlivePacketServerbound)
        assert packet.keep_alive_id == keep_alive_id

        packet = packets.DisconnectPacketPlayState(
            self.context, json_data=json.dumps({'text': 'Test complete.'}))
        self.write_packet(packet, client_socket)
        return False

    def run_status(self, client_socket, client_file):
        self.packets = self.packets_status

        packet = self.read_packet(client_file)
        assert isinstance(packet, packets.RequestPacket)

        packet = packets.ResponsePacket(self.context)
        packet.json_response = json.dumps({
            'version': {
                'name':     self.minecraft_version,
                'protocol': self.context.protocol_version},
            'players': {
                'max':      1,
                'online':   0,
                'sample':   []},
            'description': {
                'text':     'FakeServer'}})
        self.write_packet(packet, client_socket)

        try:
            packet = self.read_packet(client_file)
        except EOFError:
            return False
        assert isinstance(packet, packets.PingPacket)

        res_packet = packets.PingPacketResponse(self.context)
        res_packet.time = packet.time
        self.write_packet(res_packet, client_socket)
        return False

    def read_packet_filtered(self, client_file):
        while True:
            packet = self.read_packet(client_file)
            if isinstance(packet, packets.PositionAndLookPacket):
                continue
            if isinstance(packet, packets.AnimationPacketServerbound):
                continue
            return packet

    def read_packet(self, client_file):
        buffer = self.read_packet_buffer(client_file)
        packet_id = types.VarInt.read(buffer)
        if packet_id in self.packets:
            packet = self.packets[packet_id](self.context)
            packet.read(buffer)
        else:
            packet = packets.Packet(self.context, id=packet_id)
        logging.debug('[ ->S] %s' % packet)
        return packet

    def read_packet_buffer(self, client_file):
        length = types.VarInt.read(client_file)
        buffer = packets.PacketBuffer()
        while len(buffer.get_writable()) < length:
            buffer.send(client_file.read(length - len(buffer.get_writable())))
        buffer.reset_cursor()
        return buffer

    def write_packet(self, packet, client_socket):
        packet.write(client_socket)
        logging.debug('[S-> ] %s' % packet)

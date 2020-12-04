import pynbt

from minecraft import SUPPORTED_MINECRAFT_VERSIONS
from minecraft.networking import connection
from minecraft.networking import types
from minecraft.networking import packets
from minecraft.networking.packets import clientbound
from minecraft.networking.packets import serverbound
from minecraft.networking.encryption import (
    create_AES_cipher, EncryptedFileObjectWrapper, EncryptedSocketWrapper
)

from cryptography.hazmat.primitives.asymmetric.padding import PKCS1v15

from numbers import Integral
import unittest
import threading
import logging
import socket
import json
import sys
import zlib
import hashlib
import uuid


THREAD_TIMEOUT_S = 2


class FakeClientDisconnect(Exception):
    """ Raised by 'FakeClientHandler.read_packet' if the client has cleanly
        disconnected prior to the call.
    """


class FakeServerDisconnect(Exception):
    """ May be raised within 'FakeClientHandler.handle_*' in order to terminate
        the client's connection. 'message' is provided as an argument to
        'handle_play_server_disconnect' or 'handle_login_server_disconnect'.
    """
    def __init__(self, message=None):
        self.message = message


class FakeServerTestSuccess(Exception):
    """ May be raised from within 'FakeClientHandler.handle_*' or from a
        'Connection' packet listener in order to terminate a 'FakeServerTest'
        successfully.
    """


class FakeClientHandler(object):
    """ Represents a single client connection being handled by a 'FakeServer'.
        The methods of the form 'handle_*' may be overridden by subclasses to
        customise the behaviour of the server.
    """

    __slots__ = 'server', 'socket', 'socket_file', 'packets', \
                'compression_enabled', 'user_uuid', 'user_name'

    def __init__(self, server, socket):
        self.server = server
        self.socket = socket
        self.socket_file = socket.makefile('rb', 0)
        self.compression_enabled = False
        self.user_uuid = None
        self.user_name = None

    def run(self):
        # Communicate with the client until disconnected.
        try:
            self._run_handshake()
            try:
                self.socket.shutdown(socket.SHUT_RDWR)
            except IOError:
                pass
        except (FakeClientDisconnect, BrokenPipeError) as exc:
            if not self.handle_abnormal_disconnect(exc):
                raise
        finally:
            self.socket.close()
            self.socket_file.close()

    def handle_abnormal_disconnect(self, exc):
        # Called when the client disconnects in an abnormal fashion. If this
        # handler returns True, the error is ignored and is treated as a normal
        # disconnection.
        return False

    def handle_connection(self):
        # Called in the handshake state, just after the client connects,
        # before any packets have been exchanged.
        pass

    def handle_handshake(self, handshake_packet):
        # Called in the handshake state, after receiving the client's
        # Handshake packet, which is provided as an argument.
        pass

    def handle_login(self, login_start_packet):
        # Called to transition from the login state to the play state, after
        # compression and encryption, if applicable, have been set up. The
        # client's LoginStartPacket is given as an argument.
        self.user_name = login_start_packet.name
        self.user_uuid = uuid.UUID(bytes=hashlib.md5(
            ('OfflinePlayer:%s' % self.user_name).encode('utf8')).digest())
        self.write_packet(clientbound.login.LoginSuccessPacket(
            UUID=str(self.user_uuid), Username=self.user_name))

    def handle_play_start(self):
        # Called upon entering the play state.
        packet = clientbound.play.JoinGamePacket(
            entity_id=0, is_hardcore=False, game_mode=0, previous_game_mode=0,
            world_names=['minecraft:overworld'],
            world_name='minecraft:overworld',
            hashed_seed=12345, difficulty=2, max_players=1,
            level_type='default', reduced_debug_info=False, render_distance=9,
            respawn_screen=False, is_debug=False, is_flat=False)

        if self.server.context.protocol_later_eq(748):
            packet.dimension = pynbt.TAG_Compound({
                'natural': pynbt.TAG_Byte(1),
                'effects': pynbt.TAG_String('minecraft:overworld'),
            }, '')
            packet.dimension_codec = pynbt.TAG_Compound({
                'minecraft:dimension_type': pynbt.TAG_Compound({
                    'type': pynbt.TAG_String('minecraft:dimension_type'),
                    'value': pynbt.TAG_List(pynbt.TAG_Compound, [
                        pynbt.TAG_Compound(packet.dimension),
                    ]),
                }),
                'minecraft:worldgen/biome': pynbt.TAG_Compound({
                    'type': pynbt.TAG_String('minecraft:worldgen/biome'),
                    'value': pynbt.TAG_List(pynbt.TAG_Compound, [
                        pynbt.TAG_Compound({
                            'id': pynbt.TAG_Int(1),
                            'name': pynbt.TAG_String('minecraft:plains'),
                        }),
                        pynbt.TAG_Compound({
                            'id': pynbt.TAG_Int(2),
                            'name': pynbt.TAG_String('minecraft:desert'),
                        }),
                    ]),
                }),
            }, '')
        elif self.server.context.protocol_later_eq(718):
            packet.dimension = 'minecraft:overworld'
        else:
            packet.dimension = types.Dimension.OVERWORLD

        self.write_packet(packet)

    def handle_play_packet(self, packet):
        # Called upon each packet received after handle_play_start() returns.
        if isinstance(packet, serverbound.play.ChatPacket):
            assert len(packet.message) <= packet.max_length
            self.write_packet(clientbound.play.ChatMessagePacket(json.dumps({
                'translate': 'chat.type.text',
                'with': [self.username, packet.message],
            })))

    def handle_status(self, request_packet):
        # Called in the first phase of the status state, to send the Response
        # packet. The client's Request packet is provided as an argument.
        packet = clientbound.status.ResponsePacket()
        packet.json_response = json.dumps({
            'version': {
                'name':     self.server.minecraft_version,
                'protocol': self.server.context.protocol_version},
            'players': {
                'max':      1,
                'online':   0,
                'sample':   []},
            'description': {
                'text':     'FakeServer'}})
        self.write_packet(packet)

    def handle_ping(self, ping_packet):
        # Called in the second phase of the status state, to respond to a Ping
        # packet, which is provided as an argument.
        packet = clientbound.status.PingResponsePacket(time=ping_packet.time)
        self.write_packet(packet)

    def handle_login_server_disconnect(self, message):
        # Called when the server cleanly terminates the connection during
        # login, i.e. by raising FakeServerDisconnect from a handler.
        message = 'Connection denied.' if message is None else message
        self.write_packet(clientbound.login.DisconnectPacket(
            json_data=json.dumps({'text': message})))

    def handle_play_server_disconnect(self, message):
        # As 'handle_login_server_disconnect', but for the play state.
        message = 'Disconnected.' if message is None else message
        self.write_packet(clientbound.play.DisconnectPacket(
            json_data=json.dumps({'text': message})))

    def handle_play_client_disconnect(self):
        # Called when the client cleanly terminates the connection during play.
        pass

    def write_packet(self, packet):
        # Send and log a clientbound packet.
        packet.context = self.server.context
        logging.debug('[S-> ] %s' % packet)
        packet.write(self.socket, **(
            {'compression_threshold': self.server.compression_threshold}
            if self.compression_enabled else {}))

    def read_packet(self):
        # Read and log a serverbound packet from the client, or raises
        # FakeClientDisconnect if the client has cleanly disconnected.
        buffer = self._read_packet_buffer()
        packet_id = types.VarInt.read(buffer)
        if packet_id in self.packets:
            packet = self.packets[packet_id](self.server.context)
            packet.read(buffer)
        else:
            packet = packets.Packet(self.server.context, id=packet_id)
        logging.debug('[ ->S] %s' % packet)
        return packet

    def _run_handshake(self):
        # Enter the initial (i.e. handshaking) state of the connection.
        self.packets = self.server.packets_handshake
        try:
            self.handle_connection()
            packet = self.read_packet()
            assert isinstance(packet, serverbound.handshake.HandShakePacket), \
                   type(packet)
            self.handle_handshake(packet)
            if packet.next_state == 1:
                self._run_status()
            elif packet.next_state == 2:
                self._run_handshake_play(packet)
            else:
                raise AssertionError('Unknown state: %s' % packet.next_state)
        except FakeServerDisconnect:
            pass

    def _run_handshake_play(self, packet):
        # Prepare to transition from handshaking to play state (via login),
        # using the given serverbound HandShakePacket to perform play-specific
        # processing.
        if self.server.context.protocol_version == packet.protocol_version:
            return self._run_login()
        elif self.server.context.protocol_earlier(packet.protocol_version):
            msg = "Outdated server! I'm still on %s" \
                  % self.server.minecraft_version
        else:
            msg = 'Outdated client! Please use %s' \
                  % self.server.minecraft_version
        self.handle_login_server_disconnect(msg)

    def _run_login(self):
        # Enter the login state of the connection.
        self.packets = self.server.packets_login
        packet = self.read_packet()
        assert isinstance(packet, serverbound.login.LoginStartPacket)

        if self.server.private_key is not None:
            self._run_login_encryption()

        if self.server.compression_threshold is not None:
            self.write_packet(clientbound.login.SetCompressionPacket(
                threshold=self.server.compression_threshold))
            self.compression_enabled = True

        try:
            self.handle_login(packet)
        except FakeServerDisconnect as e:
            self.handle_login_server_disconnect(message=e.message)
        else:
            self._run_playing()

    def _run_login_encryption(self):
        # Set up protocol encryption with the client, then return.
        server_token = b'\x89\x82\x9a\x01'  # Guaranteed to be random.
        self.write_packet(clientbound.login.EncryptionRequestPacket(
            server_id='', verify_token=server_token,
            public_key=self.server.public_key_bytes))

        packet = self.read_packet()
        assert isinstance(packet, serverbound.login.EncryptionResponsePacket)
        private_key = self.server.private_key
        client_token = private_key.decrypt(packet.verify_token, PKCS1v15())
        assert client_token == server_token
        shared_secret = private_key.decrypt(packet.shared_secret, PKCS1v15())

        cipher = create_AES_cipher(shared_secret)
        enc, dec = cipher.encryptor(), cipher.decryptor()
        self.socket = EncryptedSocketWrapper(self.socket, enc, dec)
        self.socket_file = EncryptedFileObjectWrapper(self.socket_file, dec)

    def _run_playing(self):
        # Enter the playing state of the connection.
        self.packets = self.server.packets_playing
        client_disconnected = False
        try:
            self.handle_play_start()
            try:
                while True:
                    self.handle_play_packet(self.read_packet())
            except FakeClientDisconnect:
                client_disconnected = True
                self.handle_play_client_disconnect()
        except FakeServerDisconnect as e:
            if not client_disconnected:
                self.handle_play_server_disconnect(message=e.message)

    def _run_status(self):
        # Enter the status state of the connection.
        self.packets = self.server.packets_status

        packet = self.read_packet()
        assert isinstance(packet, serverbound.status.RequestPacket)
        try:
            self.handle_status(packet)
            try:
                packet = self.read_packet()
            except FakeClientDisconnect:
                return
            assert isinstance(packet, serverbound.status.PingPacket)
            self.handle_ping(packet)
        except FakeServerDisconnect:
            pass

    def _read_packet_buffer(self):
        # Read a serverbound packet in the form of a raw buffer, or raises
        # FakeClientDisconnect if the client has cleanly disconnected.
        try:
            length = types.VarInt.read(self.socket_file)
        except EOFError:
            raise FakeClientDisconnect
        buffer = packets.PacketBuffer()
        while len(buffer.get_writable()) < length:
            data = self.socket_file.read(length - len(buffer.get_writable()))
            buffer.send(data)
        buffer.reset_cursor()
        if self.compression_enabled:
            data_length = types.VarInt.read(buffer)
            if data_length > 0:
                data = zlib.decompress(buffer.read())
                assert len(data) == data_length, \
                    '%s != %s' % (len(data), data_length)
                buffer.reset()
                buffer.send(data)
                buffer.reset_cursor()
        return buffer


class FakeServer(object):
    """
        A rudimentary implementation of a Minecraft server, suitable for
        testing features of minecraft.networking.connection.Connection that
        require a full connection to be established.

        The server listens on a local TCP socket and accepts client connections
        in serial, in a single-threaded manner. It responds to status queries,
        performs handshake and login, and, by default, echoes any chat messages
        back to the client until it disconnects.

        The behaviour of the server can be customised by writing subclasses of
        FakeClientHandler, overriding its public methods of the form
        'handle_*', and providing the class to the FakeServer as its
        'client_handler_type'.

        If 'private_key' is not None, it must be an instance of
        'cryptography.hazmat.primitives.asymmetric.rsa.RSAPrivateKey',
        'public_key_bytes' must be the corresponding public key serialised in
        DER format with PKCS1 encoding, and encryption will be enabled for all
        client sessions; otherwise, if it is None, encryption is disabled.
    """

    __slots__ = 'listen_socket', 'compression_threshold', 'context', \
                'minecraft_version', 'client_handler_type', 'server_type', \
                'packets_handshake', 'packets_login', 'packets_playing', \
                'packets_status', 'lock', 'stopping', 'private_key', \
                'public_key_bytes', 'test_case'

    def __init__(self, minecraft_version=None, compression_threshold=None,
                 client_handler_type=FakeClientHandler, private_key=None,
                 public_key_bytes=None, test_case=None):
        if minecraft_version is None:
            minecraft_version = list(SUPPORTED_MINECRAFT_VERSIONS.keys())[-1]

        if isinstance(minecraft_version, Integral):
            proto = minecraft_version
            minecraft_version = 'FakeVersion%d' % proto
            for ver, ver_proto in SUPPORTED_MINECRAFT_VERSIONS.items():
                if ver_proto == proto:
                    minecraft_version = ver
        else:
            proto = SUPPORTED_MINECRAFT_VERSIONS[minecraft_version]
        self.context = connection.ConnectionContext(protocol_version=proto)

        self.minecraft_version = minecraft_version
        self.compression_threshold = compression_threshold
        self.client_handler_type = client_handler_type
        self.private_key = private_key
        self.public_key_bytes = public_key_bytes
        self.test_case = test_case

        self.packets_handshake = {
            p.get_id(self.context): p for p in
            serverbound.handshake.get_packets(self.context)}

        self.packets_login = {
            p.get_id(self.context): p for p in
            serverbound.login.get_packets(self.context)}

        self.packets_playing = {
            p.get_id(self.context): p for p in
            serverbound.play.get_packets(self.context)}

        self.packets_status = {
            p.get_id(self.context): p for p in
            serverbound.status.get_packets(self.context)}

        self.listen_socket = socket.socket()
        self.listen_socket.settimeout(0.1)
        self.listen_socket.bind(('localhost', 0))
        self.listen_socket.listen(1)

        self.lock = threading.Lock()
        self.stopping = False

        super(FakeServer, self).__init__()

    def run(self):
        try:
            while True:
                try:
                    client_socket, addr = self.listen_socket.accept()
                    logging.debug('[ ++ ] Client %s connected.' % (addr,))
                    self.client_handler_type(self, client_socket).run()
                    logging.debug('[ -- ] Client %s disconnected.' % (addr,))
                except socket.timeout:
                    pass
                with self.lock:
                    if self.stopping:
                        logging.debug('[ ** ] Server stopped normally.')
                        break
        finally:
            self.listen_socket.close()

    def stop(self):
        with self.lock:
            self.stopping = True


class _FakeServerTest(unittest.TestCase):
    """
        A template for test cases involving a single client connecting to a
        single 'FakeServer'. The default behaviour causes the client to connect
        to the server, join the game, then disconnect, considering it a success
        if a 'JoinGamePacket' is received before a 'DisconnectPacket'.

        Customise by making subclasses that:
         1. Override the attributes present in this class, where desired, so
            that they will apply to all tests; and
         2. Define tests (or override 'runTest') to call '_test_connect' with
            the necessary arguments to override class attributes; and
         3. Override '_start_client' in order to set event listeners and
            change the connection mode, if necessary.
        To terminate the test and indicate that it finished successfully, a
        client packet handler or a handler method of the 'FakeClientHandler'
        must raise a 'FakeServerTestSuccess' exception.
    """

    server_version = None
    # The Minecraft version ID that the server will support.
    # If None, the latest supported version will be used.

    client_versions = None
    # The set of Minecraft version IDs or protocol version numbers that the
    # client will support. If None, the client supports all possible versions.

    server_type = FakeServer
    # A subclass of FakeServer to be used in tests.

    client_handler_type = FakeClientHandler
    # A subclass of FakeClientHandler to be used in tests.

    connection_type = connection.Connection
    # The constructor of the Connection instance to be used.

    compression_threshold = None
    # The compression threshold that the server will dictate.
    # If None, compression is disabled.

    private_key = None
    # The RSA private key used by the server: see 'FakeServer'.

    public_key_bytes = None
    # The serialised RSA public key used by the server: see 'FakeServer'.

    ignore_extra_exceptions = False
    # If True, any occurrence of the 'FakeServerTestSuccess' exception is
    # considered a success, even if other exceptions are raised.

    def _start_client(self, client):
        game_joined = [False]

        def handle_join_game(packet):
            game_joined[0] = True
        client.register_packet_listener(
            handle_join_game, clientbound.play.JoinGamePacket)

        def handle_disconnect(packet):
            assert game_joined[0], 'JoinGamePacket not received.'
            raise FakeServerTestSuccess
        client.register_packet_listener(
            handle_disconnect, clientbound.play.DisconnectPacket)

        client.connect()

    def _test_connect(self, client_versions=None, server_version=None,
                      server_type=None, client_handler_type=None,
                      connection_type=None, compression_threshold=None,
                      private_key=None, public_key_bytes=None,
                      ignore_extra_exceptions=None):
        if client_versions is None:
            client_versions = self.client_versions
        if server_version is None:
            server_version = self.server_version
        if server_type is None:
            server_type = self.server_type
        if client_handler_type is None:
            client_handler_type = self.client_handler_type
        if connection_type is None:
            connection_type = self.connection_type
        if compression_threshold is None:
            compression_threshold = self.compression_threshold
        if private_key is None:
            private_key = self.private_key
        if public_key_bytes is None:
            public_key_bytes = self.public_key_bytes
        if ignore_extra_exceptions is None:
            ignore_extra_exceptions = self.ignore_extra_exceptions

        server = server_type(minecraft_version=server_version,
                             compression_threshold=compression_threshold,
                             client_handler_type=client_handler_type,
                             private_key=private_key,
                             public_key_bytes=public_key_bytes,
                             test_case=self)
        addr = "localhost"
        port = server.listen_socket.getsockname()[1]

        cond = threading.Condition()
        server_lock = threading.Lock()
        server_exc_info = [None]
        client_lock = threading.Lock()
        client_exc_info = [None]

        client = connection_type(
            addr, port, username='TestUser', allowed_versions=client_versions)

        @client.exception_handler()
        def handle_client_exception(exc, exc_info):
            with client_lock:
                client_exc_info[0] = exc_info
            with cond:
                cond.notify_all()

        @client.listener(packets.Packet, early=True)
        def handle_incoming_packet(packet):
            logging.debug('[ ->C] %s' % packet)

        @client.listener(packets.Packet, early=True, outgoing=True)
        def handle_outgoing_packet(packet):
            logging.debug('[C-> ] %s' % packet)

        server_thread = threading.Thread(
            name='FakeServer',
            target=self._test_connect_server,
            args=(server, cond, server_lock, server_exc_info))
        server_thread.daemon = True

        errors = []
        try:
            try:
                with cond:
                    server_thread.start()
                    self._start_client(client)
                    cond.wait(THREAD_TIMEOUT_S)
            finally:
                # Wait for all threads to exit.
                server.stop()
                for thread in server_thread, client.networking_thread:
                    if thread is not None and thread.is_alive():
                        thread.join(THREAD_TIMEOUT_S)
                    if thread is not None and thread.is_alive():
                        errors.append({
                            'msg': 'Thread "%s" timed out.' % thread.name})
        except Exception:
            errors.insert(0, {
                'msg': 'Exception in main thread',
                'exc_info': sys.exc_info()})
        else:
            timeout = True
            for lock, [exc_info], thread_name in (
                (client_lock, client_exc_info, 'client thread'),
                (server_lock, server_exc_info, 'server thread')
            ):
                with lock:
                    if exc_info is None:
                        continue
                    timeout = False
                    if not issubclass(exc_info[0], FakeServerTestSuccess):
                        errors.insert(0, {
                            'msg': 'Exception in %s:' % thread_name,
                            'exc_info': exc_info})
                    elif ignore_extra_exceptions:
                        del errors[:]
                        break
            if timeout:
                errors.insert(0, {'msg': 'Test timed out.'})

        if len(errors) > 1:
            for error in errors:
                logging.error(**error)
            self.fail('Multiple errors: see logging output.')
        elif errors and 'exc_info' in errors[0]:
            exc_value, exc_tb = errors[0]['exc_info'][1:]
            raise exc_value.with_traceback(exc_tb)
        elif errors:
            self.fail(errors[0]['msg'])

    def _test_connect_server(self, server, cond, server_lock, server_exc_info):
        exc_info = None
        try:
            server.run()
        except Exception:
            exc_info = sys.exc_info()
        with server_lock:
            server_exc_info[0] = exc_info
        with cond:
            cond.notify_all()

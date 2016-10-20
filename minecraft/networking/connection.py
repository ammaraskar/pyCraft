from __future__ import print_function

from collections import deque
from threading import Lock
from zlib import decompress
import threading
import socket
import time
import select
import sys
import json
import re

from future.utils import raise_

from ..compat import unicode
from .types import VarInt
from . import packets
from . import encryption
from .. import SUPPORTED_PROTOCOL_VERSIONS
from .. import SUPPORTED_MINECRAFT_VERSIONS


class ConnectionContext(object):
    """A ConnectionContext encapsulates the static configuration parameters
    shared by the Connection class with other classes, such as Packet.
    Importantly, it can be used without knowing the interface of Connection.
    """
    def __init__(self, **kwds):
        self.protocol_version = kwds.get('protocol_version')


class _ConnectionOptions(object):
    def __init__(self, address=None, port=None, compression_threshold=-1,
                 compression_enabled=False):
        self.address = address
        self.port = port
        self.compression_threshold = compression_threshold
        self.compression_enabled = compression_enabled


class Connection(object):
    """This class represents a connection to a minecraft
    server, it handles everything from connecting, sending packets to
    handling default network behaviour
    """
    def __init__(
        self,
        address,
        port,
        auth_token=None,
        username=None,
        initial_version=None,
        allowed_versions=None,
    ):
        """Sets up an instance of this object to be able to connect to a
        minecraft server.

        The connect method needs to be called in order to actually begin
        the connection

        :param address: address of the server to connect to
        :param port(int): port of the server to connect to
        :param auth_token: :class:`authentication.AuthenticationToken` object.
                           If None, no authentication is attempted and the
                           server is assumed to be running in offline mode.
        :param username: Username string; only applicable in offline mode.
        :param initial_version: A Minecraft version string or protocol version
                                number to use as a first guess when connecting
                                to the server.
        :param allowed_versions: A set of versions, each being a Minecraft
                                 version string or protocol version number,
                                 restricting the versions that the client may
                                 use in connecting to the server.
        """

        self._write_lock = Lock()
        self.networking_thread = None
        self.packet_listeners = []

        def proto_version(version):
            if isinstance(version, str):
                proto_version = SUPPORTED_MINECRAFT_VERSIONS.get(version)
            elif isinstance(version, int):
                proto_version = version
            else:
                proto_version = None
            if proto_version not in SUPPORTED_PROTOCOL_VERSIONS:
                raise ValueError('Unsupported version number: %r.' % version)
            return proto_version

        if allowed_versions is None:
            self.allowed_proto_versions = set(SUPPORTED_PROTOCOL_VERSIONS)
        else:
            allowed_version = set(map(proto_version, allowed_versions))
            self.allowed_proto_versions = allowed_version

        if initial_version is None:
            initial_proto_version = max(self.allowed_proto_versions)
        else:
            initial_proto_version = proto_version(initial_version)
        self.context = ConnectionContext(
            protocol_version=initial_proto_version)

        self.options = _ConnectionOptions()
        self.options.address = address
        self.options.port = port
        self.auth_token = auth_token
        self.username = username

        # The reactor handles all the default responses to packets,
        # it should be changed per networking state
        self.reactor = PacketReactor(self)

    def _start_network_thread(self):
        """May safely be called multiple times."""
        if self.networking_thread is None:
            self.networking_thread = NetworkingThread(self)
            self.networking_thread.start()

    def write_packet(self, packet, force=False):
        """Writes a packet to the server.

        If force is set to true, the method attempts to acquire the write lock
        and write the packet out immediately, and as such may block.

        If force is false then the packet will be added to the end of the
        packet writing queue to be sent 'as soon as possible'

        :param packet: The :class:`network.packets.Packet` to write
        :param force(bool): Specifies if the packet write should be immediate
        """
        packet.context = self.context
        if force:
            self._write_lock.acquire()
            if self.options.compression_enabled:
                packet.write(self.socket, self.options.compression_threshold)
            else:
                packet.write(self.socket)
            self._write_lock.release()
        else:
            self._outgoing_packet_queue.append(packet)

    def register_packet_listener(self, method, *args):
        """
        Registers a listener method which will be notified when a packet of
        a selected type is received

        :param method: The method which will be called back with the packet
        :param args: The packets to listen for
        """
        self.packet_listeners.append(packets.PacketListener(method, *args))

    def _pop_packet(self):
        # Pops the topmost packet off the outgoing queue and writes it out
        # through the socket
        #
        # Mostly an internal convenience function, caller should make sure
        # they have the write lock acquired to avoid issues caused by
        # asynchronous access to the socket.
        # This should be the only method that removes elements from the
        # outbound queue
        if len(self._outgoing_packet_queue) == 0:
            return False
        else:
            packet = self._outgoing_packet_queue.popleft()
            if self.options.compression_enabled:
                packet.write(self.socket, self.options.compression_threshold)
            else:
                packet.write(self.socket)
            return True

    def status(self):
        self._connect()
        self._handshake(1)
        self._start_network_thread()
        self.reactor = StatusReactor(self)

        request_packet = packets.RequestPacket()
        self.write_packet(request_packet)

    def connect(self):
        """
        Attempt to begin connecting to the server.
        May safely be called multiple times after the first, i.e. to reconnect.
        """
        with self._write_lock:
            # We hold the lock throughout, as connect() may be called by both
            # the network thread and a parent thread simultaneously, during
            # automatic version negotiation.

            self.spawned = False
            self._outgoing_packet_queue = deque()

            self._connect()
            self._handshake()
            login_start_packet = packets.LoginStartPacket()
            if self.auth_token:
                login_start_packet.name = self.auth_token.profile.name
            else:
                login_start_packet.name = self.username
            self.write_packet(login_start_packet)

            self.reactor = LoginReactor(self)
            self._start_network_thread()

    def _connect(self):
        # Connect a socket to the server and create a file object from the
        # socket.
        # The file object is used to read any and all data from the socket
        # since it's "guaranteed" to read the number of bytes specified,
        # the socket itself will mostly be used to write data upstream to
        # the server.
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.options.address, self.options.port))
        self.file_object = self.socket.makefile("rb", 0)

    def _handshake(self, next_state=2):
        handshake = packets.HandShakePacket()
        handshake.protocol_version = self.context.protocol_version
        handshake.server_address = self.options.address
        handshake.server_port = self.options.port
        handshake.next_state = next_state

        self.write_packet(handshake)


class NetworkingThread(threading.Thread):
    def __init__(self, connection):
        threading.Thread.__init__(self)
        self.interrupt = False
        self.connection = connection
        self.name = "Networking Thread"
        self.daemon = True

    def run(self):
        try:
            self._run()
        except:
            ty, ex, tb = sys.exc_info()
            ex.exc_info = ty, ex, tb
            self.connection.exception = ex

    def _run(self):
        while True:
            if self.interrupt:
                break

            # Attempt to write out as many as 300 packets as possible every
            # 0.05 seconds (20 ticks per second)
            num_packets = 0
            self.connection._write_lock.acquire()
            try:
                while self.connection._pop_packet():
                    num_packets += 1
                    if num_packets >= 300:
                        break
                exc_info = None
            except:
                exc_info = sys.exc_info()
            self.connection._write_lock.release()

            # Read and react to as many as 50 packets
            num_packets = 0
            packet = self.connection.reactor.read_packet(
                self.connection.file_object)
            while packet:
                num_packets += 1

                # Do not raise an IOError if it occurred while a disconnect
                # packet was received, as this may be part of an orderly
                # disconnection.
                if packet.packet_name == 'disconnect' and \
                   exc_info is not None and \
                   isinstance(exc_info[1], IOError):
                    exc_info = None

                try:
                    self.connection.reactor.react(packet)
                    for listener in self.connection.packet_listeners:
                        listener.call_packet(packet)
                except IgnorePacket:
                    pass

                if num_packets >= 50:
                    break

                packet = self.connection.reactor.read_packet(
                    self.connection.file_object)

            if exc_info is not None:
                raise_(*exc_info)

            time.sleep(0.05)


class IgnorePacket(Exception):
    """
    This exception may be raised from within a packet handler, such as
    `PacketReactor.react' or a packet listener added with
    `Connection.register_packet_listener', to stop any subsequent handlers from
    being called on that particular packet.
    """
    pass


class PacketReactor(object):
    """
    Reads and reacts to packets
    """
    state_name = None
    TIME_OUT = 0

    get_clientbound_packets = staticmethod(lambda context: set())

    def __init__(self, connection):
        self.connection = connection
        context = self.connection.context
        self.clientbound_packets = {
            packet.get_id(context): packet
            for packet in self.__class__.get_clientbound_packets(context)}

    def read_packet(self, stream):
        ready_to_read = select.select([stream], [], [], self.TIME_OUT)[0]

        if ready_to_read:
            length = VarInt.read(stream)

            packet_data = packets.PacketBuffer()
            packet_data.send(stream.read(length))
            # Ensure we read all the packet
            while len(packet_data.get_writable()) < length:
                packet_data.send(
                    stream.read(length - len(packet_data.get_writable())))
            packet_data.reset_cursor()

            if self.connection.options.compression_enabled:
                decompressed_size = VarInt.read(packet_data)
                if decompressed_size > 0:
                    decompressed_packet = decompress(packet_data.read())
                    assert len(decompressed_packet) == decompressed_size, \
                        'decompressed length %d, but expected %d' % \
                        (len(decompressed_packet), decompressed_size)
                    packet_data.reset()
                    packet_data.send(decompressed_packet)
                    packet_data.reset_cursor()

            packet_id = VarInt.read(packet_data)

            # If we know the structure of the packet, attempt to parse it
            # otherwise just skip it
            if packet_id in self.clientbound_packets:
                packet = self.clientbound_packets[packet_id]()
                packet.context = self.connection.context
                packet.read(packet_data)
                return packet
            else:
                return packets.Packet(context=self.connection.context)
        else:
            return None

    def react(self, packet):
        raise NotImplementedError("Call to base reactor")


class LoginReactor(PacketReactor):
    get_clientbound_packets = staticmethod(packets.state_login_clientbound)

    def react(self, packet):
        if packet.packet_name == "encryption request":

            secret = encryption.generate_shared_secret()
            token, encrypted_secret = encryption.encrypt_token_and_secret(
                packet.public_key, packet.verify_token, secret)

            # A server id of '-' means the server is in offline mode
            if packet.server_id != '-':
                server_id = encryption.generate_verification_hash(
                    packet.server_id, secret, packet.public_key)
                if self.connection.auth_token is not None:
                    self.connection.auth_token.join(server_id)

            encryption_response = packets.EncryptionResponsePacket()
            encryption_response.shared_secret = encrypted_secret
            encryption_response.verify_token = token

            # Forced because we'll have encrypted the connection by the time
            # it reaches the outgoing queue
            self.connection.write_packet(encryption_response, force=True)

            # Enable the encryption
            cipher = encryption.create_AES_cipher(secret)
            encryptor = cipher.encryptor()
            decryptor = cipher.decryptor()
            self.connection.socket = encryption.EncryptedSocketWrapper(
                self.connection.socket, encryptor, decryptor)
            self.connection.file_object = \
                encryption.EncryptedFileObjectWrapper(
                    self.connection.file_object, decryptor)

        if packet.packet_name == "disconnect":
            # Test for a disconnect packet indicating a version mismatch.
            # (Note: it is known how the disconnect messages are formatted for
            # official servers within SUPPORTED_MINECRAFT_VERSIONS, but in case
            # new versions are added, this section may need to be updated.)
            try:
                data = json.loads(packet.json_data)
            except ValueError:
                pass
            if isinstance(data, dict) and 'text' in data:
                data = data['text']
            if not isinstance(data, (str, unicode)):
                return
            match = re.match(
                r"(Outdated client! Please use"
                r"|Outdated server! I'm still on) (?P<version>.*)", data)
            if not match:
                # If there's no match, we will try to select random version
                version = random.choice(list(SUPPORTED_MINECRAFT_VERSIONS.keys()))
            else:
                version = match.group('version')
            self.connection.allowed_proto_versions.remove(
                self.connection.context.protocol_version)
            
            if not version:
                return
            # If there's no versions left to try
            if not self.connection.allowed_proto_versions:
                return
            if version in SUPPORTED_MINECRAFT_VERSIONS:
                new_version = SUPPORTED_MINECRAFT_VERSIONS[version]
            elif data.startswith('Outdated client!'):
                new_version = max(SUPPORTED_PROTOCOL_VERSIONS)
            elif data.startswith('Outdated server!'):
                new_version = min(SUPPORTED_PROTOCOL_VERSIONS)
            if new_version in self.connection.allowed_proto_versions:
                # Ignore this disconnect packet and reconnect with the new
                # protocol version, making it appear (on the client side) as if
                # the client had initially connected with the (hopefully)
                # correct version.
                self.connection.context.protocol_version = new_version
                self.connection.connect()
                raise IgnorePacket

        if packet.packet_name == "login success":
            self.connection.reactor = PlayingReactor(self.connection)

        if packet.packet_name == "set compression":
            self.connection.options.compression_threshold = packet.threshold
            self.connection.options.compression_enabled = True


class PlayingReactor(PacketReactor):
    get_clientbound_packets = staticmethod(packets.state_playing_clientbound)

    def react(self, packet):
        if packet.packet_name == "set compression":
            self.connection.options.compression_threshold = packet.threshold
            self.connection.options.compression_enabled = True

        if packet.packet_name == "keep alive":
            keep_alive_packet = packets.KeepAlivePacketServerbound()
            keep_alive_packet.keep_alive_id = packet.keep_alive_id
            self.connection.write_packet(keep_alive_packet)

        if packet.packet_name == "player position and look":
            teleport_confirm = packets.TeleportConfirmPacket()
            teleport_confirm.teleport_id = packet.teleport_id
            self.connection.write_packet(teleport_confirm)
            '''
            position_response = packets.PositionAndLookPacket()
            position_response.x = packet.x
            position_response.feet_y = packet.y
            position_response.z = packet.z
            position_response.yaw = packet.yaw
            position_response.pitch = packet.pitch
            position_response.on_ground = True
            self.connection.write_packet(position_response)
            '''
            self.connection.spawned = True

        '''
        if packet.packet_name == "disconnect":
            print(packet.json_data)  # TODO: handle propagating this back
        '''


class StatusReactor(PacketReactor):
    get_clientbound_packets = staticmethod(packets.state_status_clientbound)

    def react(self, packet):
        if packet.packet_name == "response":
            print(json.loads(packet.json_response))

            ping_packet = packets.PingPacket()
            ping_packet.time = int(time.time())
            self.connection.write_packet(ping_packet)

            self.connection.networking_thread.interrupt = True
            # TODO: More shutdown? idk

from collections import deque
from threading import Lock
from zlib import decompress
import threading
import socket
import time
import select
import sys

from .types import VarInt
from . import packets
from . import encryption
from .. import PROTOCOL_VERSION


class _ConnectionOptions(object):
    def __init__(self,
        address=None,
        port=None,
        compression_threshold=-1,
        compression_enabled=False
    ):
        self.address = address
        self.port = port
        self.compression_threshold = compression_threshold
        self.compression_enabled = compression_enabled


class Connection(object):
    """This class represents a connection to a minecraft
    server, it handles everything from connecting, sending packets to
    handling default network behaviour
    """
    def __init__(self, address, port, auth_token):
        """Sets up an instance of this object to be able to connect to a
        minecraft server.

        The connect method needs to be called in order to actually begin
        the connection

        :param address: address of the server to connect to
        :param port(int): port of the server to connect to
        :param auth_token: :class:`authentication.AuthenticationToken` object.
        """

        self._outgoing_packet_queue = deque()
        self._write_lock = Lock()
        self.networking_thread = None
        self.packet_listeners = []
    
        #: Indicates if this connection is spawned in the Minecraft game world
        self.spawned = False

        self.options = _ConnectionOptions()
        self.options.address = address
        self.options.port = port
        self.auth_token = auth_token

        # The reactor handles all the default responses to packets,
        # it should be changed per networking state
        self.reactor = PacketReactor(self)

    def _start_network_thread(self):
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
        """Attempt to begin connecting to the server
        """
        self._connect()
        self._handshake()

        self.reactor = LoginReactor(self)
        self._start_network_thread()
        login_start_packet = packets.LoginStartPacket()
        login_start_packet.name = self.auth_token.profile.name
        self.write_packet(login_start_packet)

    def _connect(self):
        # Connect a socket to the server and create a file object from the
        # socket.
        # The file object is used to read any and all data from the socket
        # since it's "guaranteed" to read the number of bytes specified,
        # the socket itself will mostly be used to write data upstream to
        # the server.
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.options.address, self.options.port))
        self.file_object = self.socket.makefile("rb")

    def _handshake(self, next_state=2):
        handshake = packets.HandShakePacket()
        handshake.protocol_version = PROTOCOL_VERSION
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
            while self.connection._pop_packet():
                num_packets += 1
                if num_packets >= 300:
                    break
            self.connection._write_lock.release()

            # Read and react to as many as 50 packets
            num_packets = 0
            packet = self.connection.reactor.read_packet(
                self.connection.file_object)
            while packet:
                num_packets += 1

                self.connection.reactor.react(packet)
                for listener in self.connection.packet_listeners:
                    listener.call_packet(packet)

                if num_packets >= 50:
                    break
                packet = self.connection.reactor.read_packet(
                    self.connection.file_object)

            time.sleep(0.05)


class PacketReactor(object):
    """
    Reads and reacts to packets
    """
    state_name = None
    clientbound_packets = None
    TIME_OUT = 0

    def __init__(self, connection):
        self.connection = connection

    def read_packet(self, stream):
        ready_to_read = select.select([self.connection.socket], [], [],
                                      self.TIME_OUT)[0]

        if self.connection.socket in ready_to_read:
            length = VarInt.read_socket(self.connection.socket)

            packet_data = packets.PacketBuffer()
            packet_data.send(stream.read(length))
            # Ensure we read all the packet
            while len(packet_data.get_writable()) < length:
                packet_data.send(
                    stream.read(length - len(packet_data.get_writable())))
            packet_data.reset_cursor()

            if self.connection.options.compression_enabled:
                compressed_size = VarInt.read(packet_data)

                if compressed_size > 0:
                    decompressed_packet = decompress(
                        packet_data.read(compressed_size))
                    packet_data.reset()
                    packet_data.send(decompressed_packet)
                    packet_data.reset_cursor()

            packet_id = VarInt.read(packet_data)

            # If we know the structure of the packet, attempt to parse it
            # otherwise just skip it
            if packet_id in self.clientbound_packets:
                packet = self.clientbound_packets[packet_id]()
                packet.read(packet_data)
                return packet
            else:
                return packets.Packet()
        else:
            return None

    def react(self, packet):
        raise NotImplementedError("Call to base reactor")


class LoginReactor(PacketReactor):
    clientbound_packets = packets.STATE_LOGIN_CLIENTBOUND

    def react(self, packet):
        if packet.packet_name == "encryption request":

            secret = encryption.generate_shared_secret()
            token, encrypted_secret = encryption.encrypt_token_and_secret(
                packet.public_key, packet.verify_token, secret)

            # A server id of '-' means the server is in offline mode
            if packet.server_id != '-':
                server_id = encryption.generate_verification_hash(
                    packet.server_id, secret, packet.public_key)

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

        '''
        if packet.packet_name == "disconnect":
            print(packet.json_data)  # TODO: handle propagating this back
        '''

        if packet.packet_name == "login success":
            self.connection.reactor = PlayingReactor(self.connection)

        if packet.packet_name == "set compression":
            self.connection.options.compression_threshold = packet.threshold
            self.connection.options.compression_enabled = True


class PlayingReactor(PacketReactor):
    clientbound_packets = packets.STATE_PLAYING_CLIENTBOUND

    def react(self, packet):
        if packet.packet_name == "set compression":
            self.connection.options.compression_threshold = packet.threshold
            self.connection.options.compression_enabled = True

        if packet.packet_name == "keep alive":
            keep_alive_packet = packets.KeepAlivePacket()
            keep_alive_packet.keep_alive_id = packet.keep_alive_id
            self.connection.write_packet(keep_alive_packet)

        if packet.packet_name == "player position and look":
            position_response = packets.PositionAndLookPacket()
            position_response.x = packet.x
            position_response.feet_y = packet.y
            position_response.z = packet.z
            position_response.yaw = packet.yaw
            position_response.pitch = packet.pitch
            position_response.on_ground = True

            self.connection.write_packet(position_response)
            self.connection.spawned = True

        '''
        if packet.packet_name == "disconnect":
            print(packet.json_data)  # TODO: handle propagating this back
        '''

class StatusReactor(PacketReactor):
    clientbound_packets = packets.STATE_STATUS_CLIENTBOUND

    def react(self, packet):
        if packet.id == packets.ResponsePacket.id:
            import json

            print(json.loads(packet.json_response))

            ping_packet = packets.PingPacket()
            ping_packet.time = int(time.time())
            self.connection.write_packet(ping_packet)

            self.connection.networking_thread.interrupt = True
            # TODO: More shutdown? idk

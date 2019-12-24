from __future__ import print_function

from collections import deque
from threading import RLock
import zlib
import threading
import socket
import timeit
import select
import sys
import json
import re

from future.utils import raise_

from .types import VarInt
from .packets import clientbound, serverbound
from . import packets
from . import encryption
from .. import SUPPORTED_PROTOCOL_VERSIONS, SUPPORTED_MINECRAFT_VERSIONS
from ..exceptions import (
    VersionMismatch, LoginDisconnect, IgnorePacket, InvalidState
)


STATE_STATUS = 1
STATE_PLAYING = 2


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
        port=25565,
        auth_token=None,
        username=None,
        initial_version=None,
        allowed_versions=None,
        handle_exception=None,
        handle_exit=None,
    ):
        """Sets up an instance of this object to be able to connect to a
        minecraft server.

        The connect method needs to be called in order to actually begin
        the connection

        :param address: address of the server to connect to
        :param port(int): port of the server to connect to
        :param auth_token: :class:`minecraft.authentication.AuthenticationToken`
                           object. If None, no authentication is attempted and
                           the server is assumed to be running in offline mode.
        :param username: Username string; only applicable in offline mode.
        :param initial_version: A Minecraft version ID string or protocol
                                version number to use if the server's protocol
                                version cannot be determined. (Although it is
                                now somewhat inaccurate, this name is retained
                                for backward compatibility.)
        :param allowed_versions: A set of versions, each being a Minecraft
                                 version ID string or protocol version number,
                                 restricting the versions that the client may
                                 use in connecting to the server.
        :param handle_exception: The final exception handler. This is triggered
                                 when an exception occurs in the networking
                                 thread that is not caught normally. After
                                 any other user-registered exception handlers
                                 are run, the final exception (which may be the
                                 original exception or one raised by another
                                 handler) is passed, regardless of whether or
                                 not it was caught by another handler, to the
                                 final handler, which may be a function obeying
                                 the protocol of 'register_exception_handler';
                                 the value 'None', meaning that if the
                                 exception was otherwise uncaught, it is
                                 re-raised from the networking thread after
                                 closing the connection; or the value 'False',
                                 meaning that the exception is never re-raised.
        :param handle_exit: A function to be called when a connection to a
                            server terminates, not caused by an exception,
                            and not with the intention to automatically
                            reconnect. Exceptions raised from this function
                            will be handled by any matching exception handlers.
        """  # NOQA

        # This lock is re-entrant because it may be acquired in a re-entrant
        # manner from within an outgoing packet listener
        self._write_lock = RLock()

        self.networking_thread = None
        self.new_networking_thread = None
        self.packet_listeners = []
        self.early_packet_listeners = []
        self.outgoing_packet_listeners = []
        self.early_outgoing_packet_listeners = []
        self._exception_handlers = []

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
            allowed_versions = set(map(proto_version, allowed_versions))
            self.allowed_proto_versions = allowed_versions

        if initial_version is None:
            self.default_proto_version = max(self.allowed_proto_versions)
        else:
            self.default_proto_version = proto_version(initial_version)

        self.context = ConnectionContext(
            protocol_version=max(self.allowed_proto_versions))

        self.options = _ConnectionOptions()
        self.options.address = address
        self.options.port = port
        self.auth_token = auth_token
        self.username = username
        self.connected = False

        self.handle_exception = handle_exception
        self.exception, self.exc_info = None, None
        self.handle_exit = handle_exit

        # The reactor handles all the default responses to packets,
        # it should be changed per networking state
        self.reactor = PacketReactor(self)

    def _start_network_thread(self):
        with self._write_lock:
            if self.networking_thread is not None and \
               not self.networking_thread.interrupt or \
               self.new_networking_thread is not None:
                raise InvalidState('A networking thread is already running.')
            elif self.networking_thread is None:
                self.networking_thread = NetworkingThread(self)
                self.networking_thread.start()
            else:
                # This thread will wait until the existing thread exits, and
                # then set 'networking_thread' to itself and
                # 'new_networking_thread' to None.
                self.new_networking_thread \
                    = NetworkingThread(self, previous=self.networking_thread)
                self.new_networking_thread.start()

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
            with self._write_lock:
                self._write_packet(packet)
        else:
            self._outgoing_packet_queue.append(packet)

    def listener(self, *packet_types, **kwds):
        """
        Shorthand decorator to register a function as a packet listener.
        """
        def listener_decorator(handler_func):
            self.register_packet_listener(handler_func, *packet_types, **kwds)
            return handler_func

        return listener_decorator

    def exception_handler(self, *exc_types, **kwds):
        """
        Shorthand decorator to register a function as an exception handler.
        """
        def exception_handler_decorator(handler_func):
            self.register_exception_handler(handler_func, *exc_types, **kwds)
            return handler_func

        return exception_handler_decorator

    def register_packet_listener(self, method, *packet_types, **kwds):
        """
        Registers a listener method which will be notified when a packet of
        a selected type is received.

        If :class:`minecraft.networking.connection.IgnorePacket` is raised from
        within this method, no subsequent handlers will be called. If
        'early=True', this has the additional effect of preventing the default
        in-built action; this could break the internal state of the
        'Connection', so should be done with care. If, in addition,
        'outgoing=True', this will prevent the packet from being written to the
        network.

        :param method: The method which will be called back with the packet
        :param packet_types: The packets to listen for
        :param outgoing: If 'True', this listener will be called on outgoing
                         packets just after they are sent to the server, rather
                         than on incoming packets.
        :param early: If 'True', this listener will be called before any
                      built-in default action is carried out, and before any
                      listeners with 'early=False' are called. If
                      'outgoing=True', the listener will be called before the
                      packet is written to the network, rather than afterwards.
        """
        outgoing = kwds.pop('outgoing', False)
        early = kwds.pop('early', False)
        target = self.packet_listeners if not early and not outgoing \
            else self.early_packet_listeners if early and not outgoing \
            else self.outgoing_packet_listeners if not early \
            else self.early_outgoing_packet_listeners
        target.append(packets.PacketListener(method, *packet_types, **kwds))

    def register_exception_handler(self, handler_func, *exc_types, **kwds):
        """
        Register a function to be called when an unhandled exception occurs
        in the networking thread.

        When multiple exception handlers are registered, they act like 'except'
        clauses in a Python 'try' clause, with the earliest matching handler
        catching the exception, and any later handlers catching any uncaught
        exception raised from within an earlier handler.

        Regardless of the presence or absence of matching handlers, any such
        exception will cause the connection and the networking thread to
        terminate, the final exception handler will be called (see the
        'handle_exception' argument of the 'Connection' contructor), and the
        original exception - or the last exception raised by a handler - will
        be set as the 'exception' and 'exc_info' attributes of the
        'Connection'.

        :param handler_func: A function taking two arguments: the exception
        object 'e' as in 'except Exception as e:', and the corresponding
        3-tuple given by 'sys.exc_info()'. The return value of the function is
        ignored, but any exception raised in it replaces the original
        exception, and may be passed to later exception handlers.

        :param exc_types: The types of exceptions that this handler shall
        catch, as in 'except (exc_type_1, exc_type_2, ...) as e:'. If this is
        empty, the handler will catch all exceptions.

        :param early: If 'True', the exception handler is registered before
        any existing exception handlers in the handling order.
        """
        early = kwds.pop('early', False)
        assert not kwds, 'Unexpected keyword arguments: %r' % (kwds,)
        if early:
            self._exception_handlers.insert(0, (handler_func, exc_types))
        else:
            self._exception_handlers.append((handler_func, exc_types))

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
            self._write_packet(self._outgoing_packet_queue.popleft())
            return True

    def _write_packet(self, packet):
        # Immediately writes the given packet to the network. The caller must
        # have the write lock acquired before calling this method.
        try:
            for listener in self.early_outgoing_packet_listeners:
                listener.call_packet(packet)

            if self.options.compression_enabled:
                packet.write(self.socket, self.options.compression_threshold)
            else:
                packet.write(self.socket)

            for listener in self.outgoing_packet_listeners:
                listener.call_packet(packet)
        except IgnorePacket:
            pass

    def status(self, handle_status=None, handle_ping=False):
        """Issue a status request to the server and then disconnect.

        :param handle_status: a function to be called with the status
                              dictionary None for the default behaviour of
                              printing the dictionary to standard output, or
                              False to ignore the result.
        :param handle_ping: a function to be called with the measured latency
                            in milliseconds, None for the default handler,
                            which prints the latency to standard outout, or
                            False, to prevent measurement of the latency.
        """
        with self._write_lock:  # pylint: disable=not-context-manager
            self._check_connection()

            self._connect()
            self._handshake(next_state=STATE_STATUS)
            self._start_network_thread()

            do_ping = handle_ping is not False
            self.reactor = StatusReactor(self, do_ping=do_ping)

            if handle_status is False:
                self.reactor.handle_status = lambda *args, **kwds: None
            elif handle_status is not None:
                self.reactor.handle_status = handle_status

            if handle_ping is False:
                self.reactor.handle_ping = lambda *args, **kwds: None
            elif handle_ping is not None:
                self.reactor.handle_ping = handle_ping

            request_packet = serverbound.status.RequestPacket()
            self.write_packet(request_packet)

    def connect(self):
        """
        Attempt to begin connecting to the server.
        May safely be called multiple times after the first, i.e. to reconnect.
        """
        # Hold the lock throughout, in case connect() is called from the
        # networking thread while another connection is in progress.
        with self._write_lock:  # pylint: disable=not-context-manager
            self._check_connection()

            # It is important that this is set correctly even when connecting
            # in status mode, as some servers, e.g. SpigotMC with the
            # ProtocolSupport plugin, use it to determine the correct response.
            self.context.protocol_version = max(self.allowed_proto_versions)

            self.spawned = False
            self._connect()
            if len(self.allowed_proto_versions) == 1:
                # There is exactly one allowed protocol version, so skip the
                # process of determining the server's version, and immediately
                # connect.
                self._handshake(next_state=STATE_PLAYING)
                login_start_packet = serverbound.login.LoginStartPacket()
                if self.auth_token:
                    login_start_packet.name = self.auth_token.profile.name
                else:
                    login_start_packet.name = self.username
                self.write_packet(login_start_packet)
                self.reactor = LoginReactor(self)
            else:
                # Determine the server's protocol version by first performing a
                # status query.
                self._handshake(next_state=STATE_STATUS)
                self.write_packet(serverbound.status.RequestPacket())
                self.reactor = PlayingStatusReactor(self)
            self._start_network_thread()

    def _check_connection(self):
        if self.networking_thread is not None and \
           not self.networking_thread.interrupt or \
           self.new_networking_thread is not None:
            raise InvalidState('There is an existing connection.')

    def _connect(self):
        # Connect a socket to the server and create a file object from the
        # socket.
        # The file object is used to read any and all data from the socket
        # since it's "guaranteed" to read the number of bytes specified,
        # the socket itself will mostly be used to write data upstream to
        # the server.
        self._outgoing_packet_queue = deque()

        info = socket.getaddrinfo(self.options.address, self.options.port,
                                  0, socket.SOCK_STREAM)

        # Prefer to use IPv4 (for backward compatibility with previous
        # versions that always resolved hostnames to IPv4 addresses),
        # then IPv6, then other address families.
        def key(ai):
            return 0 if ai[0] == socket.AF_INET else \
                   1 if ai[0] == socket.AF_INET6 else 2
        ai_faml, ai_type, ai_prot, _ai_cnam, ai_addr = min(info, key=key)

        self.socket = socket.socket(ai_faml, ai_type, ai_prot)
        self.socket.connect(ai_addr)
        self.file_object = self.socket.makefile("rb", 0)
        self.options.compression_enabled = False
        self.options.compression_threshold = -1
        self.connected = True

    def disconnect(self, immediate=False):
        """Terminate the existing server connection, if there is one.
           If 'immediate' is True, do not attempt to write any packets.
        """
        with self._write_lock:  # pylint: disable=not-context-manager
            self.connected = False

            if not immediate and self.socket is not None:
                # Flush any packets remaining in the queue.
                while self._pop_packet():
                    pass

            if self.networking_thread is not None:
                self.networking_thread.interrupt = True

            if self.socket is not None:
                try:
                    self.socket.shutdown(socket.SHUT_RDWR)
                except socket.error:
                    pass
                finally:
                    self.socket.close()
                    self.socket = None

    def _handshake(self, next_state=STATE_PLAYING):
        handshake = serverbound.handshake.HandShakePacket()
        handshake.protocol_version = self.context.protocol_version
        handshake.server_address = self.options.address
        handshake.server_port = self.options.port
        handshake.next_state = next_state

        self.write_packet(handshake)

    def _handle_exception(self, exc, exc_info):
        # Call the current PacketReactor's exception handler.
        try:
            if self.reactor.handle_exception(exc, exc_info):
                return
        except Exception as new_exc:
            exc, exc_info = new_exc, sys.exc_info()

        # Call the user-registered exception handlers in order.
        for handler, exc_types in self._exception_handlers:
            if not exc_types or isinstance(exc, exc_types):
                try:
                    handler(exc, exc_info)
                    caught = True
                    break
                except Exception as new_exc:
                    exc, exc_info = new_exc, sys.exc_info()
        else:
            caught = False

        # Call the user-specified final exception handler.
        if self.handle_exception not in (None, False):
            try:
                self.handle_exception(exc, exc_info)
            except Exception as new_exc:
                exc, exc_info = new_exc, sys.exc_info()

        # For backward compatibility, try to set the 'exc_info' attribute.
        try:
            exc.exc_info = exc_info
        except (TypeError, AttributeError):
            pass

        # Record the exception and cleanly terminate the connection.
        self.exception, self.exc_info = exc, exc_info
        self.disconnect(immediate=True)

        # If allowed by the final exception handler, re-raise the exception.
        if self.handle_exception is None and not caught:
            raise_(*exc_info)

    def _version_mismatch(self, server_protocol=None, server_version=None):
        if server_protocol is None:
            server_protocol = SUPPORTED_MINECRAFT_VERSIONS.get(server_version)

        if server_protocol is None:
            vs = 'version' if server_version is None else \
                 ('version of %s' % server_version)
        else:
            vs = ('protocol version of %d' % server_protocol) + \
                 ('' if server_version is None else ' (%s)' % server_version)
        ss = 'supported, but not allowed for this connection' \
             if server_protocol in SUPPORTED_PROTOCOL_VERSIONS \
             else 'not supported'
        raise VersionMismatch("Server's %s is %s." % (vs, ss))

    def _handle_exit(self):
        if not self.connected and self.handle_exit is not None:
            self.handle_exit()

    def _react(self, packet):
        try:
            for listener in self.early_packet_listeners:
                listener.call_packet(packet)
            self.reactor.react(packet)
            for listener in self.packet_listeners:
                listener.call_packet(packet)
        except IgnorePacket:
            pass


class NetworkingThread(threading.Thread):
    def __init__(self, connection, previous=None):
        threading.Thread.__init__(self)
        self.interrupt = False
        self.connection = connection
        self.name = "Networking Thread"
        self.daemon = True

        self.previous_thread = previous

    def run(self):
        try:
            if self.previous_thread is not None:
                if self.previous_thread.is_alive():
                    self.previous_thread.join()
                with self.connection._write_lock:
                    self.connection.networking_thread = self
                    self.connection.new_networking_thread = None
            self._run()
            self.connection._handle_exit()
        except Exception as e:
            self.interrupt = True
            self.connection._handle_exception(e, sys.exc_info())
        finally:
            with self.connection._write_lock:
                self.connection.networking_thread = None

    def _run(self):
        while not self.interrupt:
            # Attempt to write out as many as 300 packets.
            num_packets = 0
            with self.connection._write_lock:
                try:
                    while not self.interrupt and self.connection._pop_packet():
                        num_packets += 1
                        if num_packets >= 300:
                            break
                    exc_info = None
                except IOError:
                    exc_info = sys.exc_info()

                # If any packets remain to be written, resume writing as soon
                # as possible after reading any available packets; otherwise,
                # wait for up to 50ms (1 tick) for new packets to arrive.
                if self.connection._outgoing_packet_queue:
                    read_timeout = 0
                else:
                    read_timeout = 0.05

            # Read and react to as many as 50 packets.
            while num_packets < 50 and not self.interrupt:
                packet = self.connection.reactor.read_packet(
                    self.connection.file_object, timeout=read_timeout)
                if not packet:
                    break
                num_packets += 1
                self.connection._react(packet)
                read_timeout = 0

                # Ignore the earlier exception if a disconnect packet is
                # received, as it may have been caused by trying to write to
                # the closed socket, which does not represent a program error.
                if exc_info is not None and packet.packet_name == "disconnect":
                    exc_info = None

            if exc_info is not None:
                raise_(*exc_info)


class PacketReactor(object):
    """
    Reads and reacts to packets
    """
    state_name = None

    # Handshaking is considered the "default" state
    get_clientbound_packets = staticmethod(clientbound.handshake.get_packets)

    def __init__(self, connection):
        self.connection = connection
        context = self.connection.context
        self.clientbound_packets = {
            packet.get_id(context): packet
            for packet in self.__class__.get_clientbound_packets(context)}

    def read_packet(self, stream, timeout=0):
        # Block for up to `timeout' seconds waiting for `stream' to become
        # readable, returning `None' if the timeout elapses.
        ready_to_read = select.select([stream], [], [], timeout)[0]

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
                    decompressor = zlib.decompressobj()
                    decompressed_packet = decompressor.decompress(
                                                       packet_data.read())
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
        """Called with each incoming packet after early packet listeners are
           run (if none of them raise 'IgnorePacket'), but before regular
           packet listeners are run. If this method raises 'IgnorePacket', no
           subsequent packet listeners will be called for this packet.
        """
        raise NotImplementedError("Call to base reactor")

    def handle_exception(self, exc, exc_info):
        """Called when an exception is raised in the networking thread. If this
           method returns True, the default action will be prevented and the
           exception ignored (but the networking thread will still terminate).
        """
        return False


class LoginReactor(PacketReactor):
    get_clientbound_packets = staticmethod(clientbound.login.get_packets)

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

            encryption_response = serverbound.login.EncryptionResponsePacket()
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

        elif packet.packet_name == "disconnect":
            # Receiving a disconnect packet in the login state indicates an
            # abnormal condition. Raise an exception explaining the situation.
            try:
                msg = json.loads(packet.json_data)['text']
            except (ValueError, TypeError, KeyError):
                msg = packet.json_data
            match = re.match(r"Outdated (client! Please use|server!"
                             r" I'm still on) (?P<ver>\S+)$", msg)
            if match:
                ver = match.group('ver')
                self.connection._version_mismatch(server_version=ver)
            raise LoginDisconnect('The server rejected our login attempt '
                                  'with: "%s".' % msg)

        elif packet.packet_name == "login success":
            self.connection.reactor = PlayingReactor(self.connection)

        elif packet.packet_name == "set compression":
            self.connection.options.compression_threshold = packet.threshold
            self.connection.options.compression_enabled = True

        elif packet.packet_name == "login plugin request":
            self.connection.write_packet(
                serverbound.login.PluginResponsePacket(
                    message_id=packet.message_id, successful=False))


class PlayingReactor(PacketReactor):
    get_clientbound_packets = staticmethod(clientbound.play.get_packets)

    def react(self, packet):
        if packet.packet_name == "set compression":
            self.connection.options.compression_threshold = packet.threshold
            self.connection.options.compression_enabled = True

        elif packet.packet_name == "keep alive":
            keep_alive_packet = serverbound.play.KeepAlivePacket()
            keep_alive_packet.keep_alive_id = packet.keep_alive_id
            self.connection.write_packet(keep_alive_packet)

        elif packet.packet_name == "player position and look":
            if self.connection.context.protocol_version >= 107:
                teleport_confirm = serverbound.play.TeleportConfirmPacket()
                teleport_confirm.teleport_id = packet.teleport_id
                self.connection.write_packet(teleport_confirm)
            else:
                position_response = serverbound.play.PositionAndLookPacket()
                position_response.x = packet.x
                position_response.feet_y = packet.y
                position_response.z = packet.z
                position_response.yaw = packet.yaw
                position_response.pitch = packet.pitch
                position_response.on_ground = True
                self.connection.write_packet(position_response)
            self.connection.spawned = True

        elif packet.packet_name == "disconnect":
            self.connection.disconnect()


class StatusReactor(PacketReactor):
    get_clientbound_packets = staticmethod(clientbound.status.get_packets)

    def __init__(self, connection, do_ping=False):
        super(StatusReactor, self).__init__(connection)
        self.do_ping = do_ping

    def react(self, packet):
        if packet.packet_name == "response":
            status_dict = json.loads(packet.json_response)
            if self.do_ping:
                ping_packet = serverbound.status.PingPacket()
                # NOTE: it may be better to depend on the `monotonic' package
                # or something similar for more accurate time measurement.
                ping_packet.time = int(1000 * timeit.default_timer())
                self.connection.write_packet(ping_packet)
            else:
                self.connection.disconnect()
            self.handle_status(status_dict)

        elif packet.packet_name == "ping":
            if self.do_ping:
                now = int(1000 * timeit.default_timer())
                self.connection.disconnect()
                self.handle_ping(now - packet.time)

    def handle_status(self, status_dict):
        print(status_dict)

    def handle_ping(self, latency_ms):
        print('Ping: %d ms' % latency_ms)


class PlayingStatusReactor(StatusReactor):
    def __init__(self, connection):
        super(PlayingStatusReactor, self).__init__(connection, do_ping=False)

    def handle_status(self, status):
        if status == {}:
            # This can occur when we connect to a Mojang server while it is
            # still initialising, so it must not cause the client to connect
            # with the default version.
            raise IOError('Invalid server status.')
        elif 'version' not in status or 'protocol' not in status['version']:
            return self.handle_failure()

        proto = status['version']['protocol']
        if proto not in self.connection.allowed_proto_versions:
            self.connection._version_mismatch(
                server_protocol=proto,
                server_version=status['version'].get('name'))

        self.handle_proto_version(proto)

    def handle_proto_version(self, proto_version):
        self.connection.allowed_proto_versions = {proto_version}
        self.connection.connect()

    def handle_failure(self):
        self.handle_proto_version(self.connection.default_proto_version)

    def handle_exception(self, exc, exc_info):
        if isinstance(exc, EOFError):
            # An exception of this type may indicate that the server does not
            # properly support status queries, so we treat it as non-fatal.
            self.connection.disconnect(immediate=True)
            self.handle_failure()
            return True

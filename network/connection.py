from collections import deque
from threading import Lock
import threading
import socket
import time
import select

from packets import *
from start import PROTOCOL_VERSION
from types import VarInt


class Connection:
    """This class represents a connection to a minecraft
    server, it handles everything from connecting, sending packets,
    handling default network behaviour
    """
    outgoing_packet_queue = deque()
    write_lock = Lock()
    networking_thread = None

    def __init__(self, address, port, login_response):
        self.address = address
        self.port = port
        self.login_response = login_response
        self.reactor = HandshakeReactor(self)

    def _start_network_thread(self):
        self.networking_thread = NetworkingThread(self)
        self.networking_thread.start()

    def write_packet(self, packet, force=False):
        if force:
            self.write_lock.acquire()
            packet.write(self.socket)
            self.write_lock.release()
        else:
            self.outgoing_packet_queue.append(packet)

    # Mostly a convenience function, caller should make sure they have the
    # write lock acquired to avoid issues caused by asynchronous access to the socket.
    # This should be the only method that removes elements from the outbound queue
    def _pop_packet(self):
        if len(self.outgoing_packet_queue) == 0:
            return False
        else:
            packet = self.outgoing_packet_queue.popleft()
            print "Writing out: " + hex(packet.id) + " / " + packet.name
            packet.write(self.socket)
            return True

    def status(self):
        self._connect()
        self._handshake(1)
        self._start_network_thread()
        self.reactor = StatusReactor(self)

        request_packet = RequestPacket()
        self.write_packet(request_packet)

    def connect(self):
        self._connect()
        self._handshake()

    def _connect(self):
        # Connect a socket to the server and create a file object from the socket
        #The file object is used to read any and all data from the socket since it's "guaranteed"
        #to read the number of bytes specified, the socket itself will mostly be
        #used to write data upstream to the server
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(20.0)
        self.socket.connect(( self.address, self.port ))
        self.file_object = self.socket.makefile()

    def _handshake(self, next_state=2):
        handshake = HandShakePacket()
        handshake.protocol_version = PROTOCOL_VERSION
        handshake.server_address = self.address
        handshake.server_port = self.port
        handshake.next_state = next_state

        handshake.write(self.socket)


class NetworkingThread(threading.Thread):
    interrupt = False

    def __init__(self, connection):
        threading.Thread.__init__(self)
        self.connection = connection
        self.name = "Networking Thread"
        self.daemon = True

    def run(self):
        while True:
            if self.interrupt:
                break
            # Attempt to write out as many as 300 packets as possible every 0.05 seconds (20 ticks per second)
            num_packets = 0
            self.connection.write_lock.acquire()
            while self.connection._pop_packet():

                self.connection._pop_packet()

                num_packets += 1
                if num_packets >= 300:
                    break
            self.connection.write_lock.release()

            # Read and react to as many as 50 packets 
            num_packets = 0
            packet = self.connection.reactor.read_packet(self.connection.file_object)
            while packet:
                num_packets += 1

                self.connection.reactor.react(packet)
                if num_packets >= 50:
                    break

                packet = self.connection.reactor.read_packet(self.connection.file_object)

            time.sleep(0.05)


class PacketReactor:
    state_name = None
    clientbound_packets = None

    TIME_OUT = 0.5

    def __init__(self, connection):
        self.connection = connection

    def read_packet(self, stream):
        ready = select.select([self.connection.socket], [], [], 0.5)
        if ready[0]:
            length = VarInt.read(stream)
            packet_id = VarInt.read(stream)

            if packet_id in self.clientbound_packets:
                packet = self.clientbound_packets[packet_id]()
                packet.read(stream)
                return packet
            else:
                print "Unkown packet: " + str(packet_id) + " / " + hex(packet_id)
                return Packet()
        else:
            return None

    def react(self, packet):
        pass


class HandshakeReactor(PacketReactor):
    clientbound_packets = state_handshake_clientbound


class StatusReactor(PacketReactor):
    clientbound_packets = state_status_clientbound

    def react(self, packet):
        if packet.id == ResponsePacket.id:
            import json

            print json.loads(packet.json_response)

            ping_packet = PingPacket()
            ping_packet.time = int(time.time())
            self.connection.write_packet(ping_packet)

            self.connection.networking_thread.interrupt = True
            # TODO: More shutdown? idk

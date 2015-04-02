from io import BytesIO
from zlib import compress

from types import *


class PacketBuffer(object):

    def __init__(self):
        self.b = BytesIO()

    def send(self, value):
        """
        Writes the given bytes to the buffer, designed to emulate socket.send
        :param value: The bytes to write
        """
        self.b.write(value)

    def read(self, length):
        return self.b.read(length)

    def reset(self):
        self.b = BytesIO()

    def reset_cursor(self):
        self.b.seek(0)

    def get_writable(self):
        return self.b.getvalue()


class PacketListener(object):

    packets_to_listen = []

    def __init__(self, callback, *args):
        self.callback = callback
        for arg in args:
            if issubclass(arg, Packet):
                self.packets_to_listen.append(arg)

    def call_packet(self, packet):
        for packet_type in self.packets_to_listen:
            if isinstance(packet, packet_type):
                self.callback(packet)


class Packet(object):

    packet_name = "base"
    id = -0x01
    definition = []

    def __init__(self):
        pass

    def read(self, file_object):
        for field in self.definition:
            for var_name, data_type in field.iteritems():
                value = data_type.read(file_object)
                setattr(self, var_name, value)

    def write(self, socket, compression_threshold=None):
        # buffer the data since we need to know the length of each packet's payload
        packet_buffer = PacketBuffer()
        # write packet's id right off the bat in the header
        VarInt.send(self.id, packet_buffer)

        for field in self.definition:
            for var_name, data_type in field.iteritems():
                data = getattr(self, var_name)
                data_type.send(data, packet_buffer)

        # compression_threshold of None means compression is disabled
        if compression_threshold is not None:
            if len(packet_buffer.get_writable()) > compression_threshold:
                # compress the current payload
                compressed_data = compress(packet_buffer.get_writable())
                packet_buffer.reset()
                # write out the length of the compressed payload
                VarInt.send(len(compressed_data), packet_buffer)
                # write the compressed payload itself
                packet_buffer.send(compressed_data)
            else:
                # write out a 0 to indicate uncompressed data
                packet_buffer.reset()
                VarInt.send(0, packet_buffer)

        VarInt.send(len(packet_buffer.get_writable()), socket)  # Packet Size
        socket.send(packet_buffer.get_writable())  # Packet Payload


# Handshake State
# ==============
class HandShakePacket(Packet):
    id = 0x00
    packet_name = "handshake"
    definition = [
        {'protocol_version': VarInt},
        {'server_address': String},
        {'server_port': UnsignedShort},
        {'next_state': VarInt}]


STATE_HANDSHAKE_CLIENTBOUND = {

}
STATE_HANDSHAKE_SERVERBOUND = {
    0x00: HandShakePacket
}


# Status State
# ==============
class ResponsePacket(Packet):
    id = 0x00
    packet_name = "response"
    definition = [
        {'json_response': String}]


class PingPacket(Packet):
    id = 0x01
    packet_name = "ping"
    definition = [
        {'time': Long}]

STATE_STATUS_CLIENTBOUND = {
    0x00: ResponsePacket,
    0x01: PingPacket
}


class RequestPacket(Packet):
    id = 0x00
    packet_name = "request"
    definition = []


class PingPacket(Packet):
    id = 0x01
    packet_name = "ping"
    definition = [
        {'time': Long}]

STATE_STATUS_SERVERBOUND = {
    0x00: RequestPacket,
    0x01: PingPacket
}


# Login State
# ==============
class DisconnectPacket(Packet):
    id = 0x00
    packet_name = "disconnect"
    definition = [
        {'json_data': String}]


class EncryptionRequestPacket(Packet):
    id = 0x01
    packet_name = "encryption request"
    definition = [
        {'server_id': String},
        {'public_key': VarIntPrefixedByteArray},
        {'verify_token': VarIntPrefixedByteArray}]


class LoginSuccessPacket(Packet):
    id = 0x02
    packet_name = "login success"
    definition = [
        {'UUID': String},
        {'Username': String}]


class SetCompressionPacket(Packet):
    id = 0x03
    packet_name = "set compression"
    definition = [
        {'threshold': VarInt}]

STATE_LOGIN_CLIENTBOUND = {
    0x00: DisconnectPacket,
    0x01: EncryptionRequestPacket,
    0x02: LoginSuccessPacket,
    0x03: SetCompressionPacket
}


class LoginStartPacket(Packet):
    id = 0x00
    packet_name = "login start"
    definition = [
        {'name': String}]


class EncryptionResponsePacket(Packet):
    id = 0x01
    packet_name = "encryption response"
    definition = [
        {'shared_secret': VarIntPrefixedByteArray},
        {'verify_token': VarIntPrefixedByteArray}]

STATE_LOGIN_SERVERBOUND = {
    0x00: LoginStartPacket,
    0x01: EncryptionResponsePacket
}


# Playing State
# ==============

class KeepAlivePacket(Packet):
    id = 0x00
    packet_name = "keep alive"
    definition = [
        {'keep_alive_id': VarInt}]


class JoinGamePacket(Packet):
    id = 0x01
    packet_name = "join game"
    definition = [
        {'entity_id': Integer},
        {'game_mode': UnsignedByte},
        {'dimension': Byte},
        {'difficulty': UnsignedByte},
        {'max_players': UnsignedByte},
        {'level_type': String},
        {'reduced_debug_info': Boolean}]


class ChatMessagePacket(Packet):
    id = 0x02
    packet_name = "chat message"
    definition = [
        {'json_data': String},
        {'position': Byte}]


class PlayerPositionAndLookPacket(Packet):
    id = 0x08
    packet_name = "player position and look"
    definition = [
        {'x': Double},
        {'y': Double},
        {'z': Double},
        {'yaw': Float},
        {'pitch': Float},
        {'flags': Byte}]


class DisconnectPacketPlayState(Packet):
    id = 0x40
    packet_name = "disconnect"

    definition = [
        {'json_data': String}]


class SetCompressionPacketPlayState(Packet):
    id = 0x46
    packet_name = "set compression"
    definition = [
        {'threshold': VarInt}]


STATE_PLAYING_CLIENTBOUND = {
    0x00: KeepAlivePacket,
    0x01: JoinGamePacket,
    0x02: ChatMessagePacket,
    0x08: PlayerPositionAndLookPacket,
    0x40: DisconnectPacketPlayState,
    0x46: SetCompressionPacketPlayState
}


class ChatPacket(Packet):
    id = 0x01
    packet_name = "chat"
    definition = [
        {'message': String}]


class PositionAndLookPacket(Packet):
    id = 0x06
    packet_name = "position and look"
    definition = [
        {'x': Double},
        {'feet_y': Double},
        {'z': Double},
        {'yaw': Float},
        {'pitch': Float},
        {'on_ground': Boolean}]

STATE_PLAYING_SERVERBOUND = {
    0x00: KeepAlivePacket,
    0x01: ChatPacket,
    0x06: PositionAndLookPacket
}
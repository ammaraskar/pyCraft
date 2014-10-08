from io import BytesIO

from types import *


class PacketBuffer(object):
    b = BytesIO()

    def send(self, value):
        self.b.write(value)

    def get_writable(self):
        return self.b.getvalue()


class Packet(object):

    name = "base"
    definition = []

    def __init__(self):
        pass

    def read(self, file_object):
        for field in self.definition:
            for var_name, data_type in field.iteritems():
                setattr(self, var_name, data_type.read(file_object))

    def write(self, socket):
        # buffer the data since we need to know the length of each packet's payload
        packet_buffer = PacketBuffer()
        # write off the id right off the bat
        VarInt.send(self.id, packet_buffer)

        for field in self.definition:
            for var_name, data_type in field.iteritems():
                data = getattr(self, var_name)
                data_type.send(data, packet_buffer)

        VarInt.send(len(packet_buffer.get_writable()), socket)  # Packet Size
        socket.send(packet_buffer.get_writable())  # Packet Payload


# Handshake State
# ==============
class HandShakePacket(Packet):
    id = 0x00
    name = "handshake"
    definition = [
        {'protocol_version': VarInt},
        {'server_address': String},
        {'server_port': UnsignedShort},
        {'next_state': VarInt}]


state_handshake_clientbound = {

}
state_handshake_serverbound = {
    0x00: HandShakePacket
}


# Status State
#==============
class ResponsePacket(Packet):
    id = 0x00
    name = "response"
    definition = [
        {'json_response': String}]


class PingPacket(Packet):
    id = 0x01
    name = "ping"
    definition = [
        {'time': Long}]


state_status_clientbound = {
    0x00: ResponsePacket,
    0x01: PingPacket
}


class RequestPacket(Packet):
    id = 0x00
    name = "request"
    definition = []


class PingPacket(Packet):
    id = 0x01
    name = "ping"
    definition = [
        {'time': Long}]


state_status_serverbound = {
    0x00: RequestPacket,
    0x01: PingPacket
}

# Login State
#==============
class DisconnectPacket(Packet):
    id = 0x00
    name = "disconnect"
    definition = [
        {'json_data': String}]


class EncryptionRequestPacket(Packet):
    id = 0x01
    name = "encryption request"
    definition = [
        {'server_id': String},
        {'public_key': ByteArray},
        {'verify_token': ByteArray}]


class LoginSucessPacket(Packet):
    id = 0x02
    name = "login success"
    definition = [
        {'UUID': String},
        {'Username': String}]


state_login_clientbound = {
    0x00: DisconnectPacket,
    0x01: EncryptionRequestPacket,
    0x02: LoginSucessPacket
}


class LoginStartPacket(Packet):
    id = 0x00
    name = "login start"
    definition = [
        {'name': String}]


class EncryptionResponsePacket(Packet):
    id = 0x01
    name = "encryption response"
    definition = [
        {'shared_secret': ByteArray},
        {'verify_token': ByteArray}]


state_login_serverbound = {
    0x00: LoginStartPacket,
    0x01: EncryptionResponsePacket
}
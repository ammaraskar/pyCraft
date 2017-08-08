from minecraft.networking.packets import Packet

from minecraft.networking.types import (
    String, VarIntPrefixedByteArray, VarInt
)


# Formerly known as state_login_clientbound.
def get_packets(context):
    packets = {
        DisconnectPacket,
        EncryptionRequestPacket,
        LoginSuccessPacket,
        SetCompressionPacket
    }
    return packets


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

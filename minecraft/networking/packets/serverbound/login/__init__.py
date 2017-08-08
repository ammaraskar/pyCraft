from minecraft.networking.packets import Packet

from minecraft.networking.types import (
    String, VarIntPrefixedByteArray
)


# Formerly known as state_login_serverbound.
def get_packets(context):
    packets = {
        LoginStartPacket,
        EncryptionResponsePacket
    }
    return packets


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

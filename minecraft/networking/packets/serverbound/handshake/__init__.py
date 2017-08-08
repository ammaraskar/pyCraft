from minecraft.networking.packets import Packet

from minecraft.networking.types import (
    VarInt, String, UnsignedShort
)


# Formerly known as state_handshake_serverbound.
def get_packets(context):
    packets = {
        HandShakePacket
    }
    return packets


class HandShakePacket(Packet):
    id = 0x00
    packet_name = "handshake"
    definition = [
        {'protocol_version': VarInt},
        {'server_address': String},
        {'server_port': UnsignedShort},
        {'next_state': VarInt}]

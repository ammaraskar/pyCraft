from .packet import Packet

from minecraft.networking.types import (
    VarInt
)


class KeepAlivePacket(Packet):
    packet_name = "keep alive"
    definition = [
        {'keep_alive_id': VarInt}]

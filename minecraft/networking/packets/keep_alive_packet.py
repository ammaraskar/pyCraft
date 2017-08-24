from .packet import Packet

from minecraft.networking.types import (
    VarInt
)


class AbstractKeepAlivePacket(Packet):
    packet_name = "keep alive"
    definition = [
        {'keep_alive_id': VarInt}]


# This alias is retained for backward compatibility:
KeepAlivePacket = AbstractKeepAlivePacket

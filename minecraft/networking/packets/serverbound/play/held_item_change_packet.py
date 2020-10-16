from minecraft.networking.packets import Packet

from minecraft.networking.types import (
    Short, BitFieldEnum
)


class HeldItemChangePacket(Packet, BitFieldEnum):
    @staticmethod
    def get_id(context):
        return 0x25

    packet_name = "held item change"

    get_definition = staticmethod(lambda context: [
        {'slot': Short}
    ])

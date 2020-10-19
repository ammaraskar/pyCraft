from minecraft.networking.packets import Packet

from minecraft.networking.types import (
    Short, BitFieldEnum
)


class HeldItemChangePacket(Packet, BitFieldEnum):
    @staticmethod
    def get_id(context):
        return 0x25 if context.protocol_version >= 738 else \
            0x24 if context.protocol_version >= 712 else \
            0x23 if context.protocol_version >= 464 else \
            0x21 if context.protocol_version >= 389 else \
            0x1F if context.protocol_version >= 386 else \
            0x1A if context.protocol_version >= 345 else \
            0x19 if context.protocol_version >= 343 else \
            0x1A if context.protocol_version >= 332 else \
            0x19 if context.protocol_version >= 318 else \
            0x17 if context.protocol_version >= 94 else \
            0x14 if context.protocol_version >= 70 else \
            0x0A if context.protocol_version >= 69 else \
            0x09

    packet_name = "held item change"

    get_definition = staticmethod(lambda context: [
        {'slot': Short}
    ])

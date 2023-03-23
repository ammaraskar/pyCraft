from minecraft.networking.packets import Packet
from minecraft.networking.types import (
    Double, Float, Boolean, Vector, multi_attribute_alias
)

class PlayerPositionPacket(Packet):
    @staticmethod
    def get_id(context):
        return 0x11 if context.protocol_version >= 471 else \
               0x12 if context.protocol_version >= 464 else \
               0x10 if context.protocol_version >= 389 else \
               0x0E if context.protocol_version >= 386 else \
               0x0D if context.protocol_version >= 345 else \
               0x0C if context.protocol_version >= 343 else \
               0x0D if context.protocol_version >= 336 else \
               0x0E if context.protocol_version >= 332 else \
               0x0D if context.protocol_version >= 318 else \
               0x0C if context.protocol_version >= 94 else \
               0x0B if context.protocol_version >= 70 else \
               0x04

    packet_name = "player position"
    definition = [
        {'x': Double},
        {'feet_y': Double},
        {'z': Double},
        {'on_ground': Boolean}
    ]

    # The code under this line was copied from the packets/clientbound/play/player_position_and_look_packet.py

    # Access the 'x', 'y', 'z' fields as a Vector tuple.
    position = multi_attribute_alias(Vector, 'x', 'feet_y', 'z')
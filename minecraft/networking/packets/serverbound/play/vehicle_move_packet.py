from minecraft.networking.packets import Packet
from minecraft.networking.types import (
    Double, Float, Vector, multi_attribute_alias, Direction, PositionAndLook
)

class VehicleMovePacket(Packet):
    @staticmethod
    def get_id(context):
        return 0x15 if context.protocol_version >= 464 else \
               0x13 if context.protocol_version >= 389 else \
               0x11 if context.protocol_version >= 386 else \
               0x10 if context.protocol_version >= 345 else \
               0x0F if context.protocol_version >= 343 else \
               0x10 if context.protocol_version >= 336 else \
               0x11 if context.protocol_version >= 318 else \
               0x10

    packet_name = "vehicle move"
    definition = [
        {'x': Double},
        {'y': Double},
        {'z': Double},
        {'yaw': Float},
        {'pitch': Float}
    ]

    # The code under this line was copied from the packets/clientbound/play/player_position_and_look_packet.py

    # Access the 'x', 'y', 'z' fields as a Vector tuple.
    position = multi_attribute_alias(Vector, 'x', 'y', 'z')

    # Access the 'yaw', 'pitch' fields as a Direction tuple.
    look = multi_attribute_alias(Direction, 'yaw', 'pitch')

    # Access the 'x', 'y', 'z', 'yaw', 'pitch' fields as a PositionAndLook.
    # NOTE: modifying the object retrieved from this property will not change
    # the packet; it can only be changed by attribute or property assignment.
    position_and_look = multi_attribute_alias(
        PositionAndLook, 'x', 'y', 'z', 'yaw', 'pitch')
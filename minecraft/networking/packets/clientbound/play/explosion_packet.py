from minecraft.networking.types import (
    Vector, Float, Byte, Integer, PrefixedArray, multi_attribute_alias, Type,
)
from minecraft.networking.packets import Packet


class ExplosionPacket(Packet):
    @staticmethod
    def get_id(context):
        return 0x1B if context.protocol_later_eq(741) else \
               0x1C if context.protocol_later_eq(721) else \
               0x1D if context.protocol_later_eq(550) else \
               0x1C if context.protocol_later_eq(471) else \
               0x1E if context.protocol_later_eq(389) else \
               0x1D if context.protocol_later_eq(345) else \
               0x1C if context.protocol_later_eq(332) else \
               0x1D if context.protocol_later_eq(318) else \
               0x1C if context.protocol_later_eq(80) else \
               0x1B if context.protocol_later_eq(67) else \
               0x27

    packet_name = 'explosion'

    class Record(Vector, Type):
        __slots__ = ()

        @classmethod
        def read(cls, file_object):
            return cls(*(Byte.read(file_object) for i in range(3)))

        @classmethod
        def send(cls, record, socket):
            for coord in record:
                Byte.send(coord, socket)

    definition = [
        {'x': Float},
        {'y': Float},
        {'z': Float},
        {'radius': Float},
        {'records': PrefixedArray(Integer, Record)},
        {'player_motion_x': Float},
        {'player_motion_y': Float},
        {'player_motion_z': Float}]

    # Access the 'x', 'y', 'z' fields as a Vector tuple.
    position = multi_attribute_alias(Vector, 'x', 'y', 'z')

    # Access the 'player_motion_{x,y,z}' fields as a Vector tuple.
    player_motion = multi_attribute_alias(
        Vector, 'player_motion_x', 'player_motion_y', 'player_motion_z')

from minecraft.networking.types import (
    Vector, Float, Byte, Integer, PrefixedArray, multi_attribute_alias, Type,
    VarInt,
)


from minecraft.networking.types import (
    Type, Boolean, UnsignedByte, Byte, Short, UnsignedShort,
    Integer, FixedPoint, FixedPointInteger, Angle, VarInt, VarLong,
    Long, UnsignedLong, Float, Double, ShortPrefixedByteArray,
    VarIntPrefixedByteArray, TrailingByteArray, String, UUID,
    Position, NBT, PrefixedArray,        
    Type, VarInt, VarLong, UnsignedLong, Integer, UnsignedByte, Position,
    Vector, MutableRecord, PrefixedArray, Boolean, attribute_alias, String
)

from minecraft.networking.packets import Packet


class UnknownPacket(Packet):
    @staticmethod
    def get_id(context):
        # return 0x20
        # return 0x16
        # return 0x4E
        return 0x4C

#      13 --> [unknown packet] 0x3C Packet
#      19 --> [unknown packet] 0x16 Packet
#      66 --> [unknown packet] 0x21 Packet
#      81 --> [unknown packet] 0x20 Packet 
#     137 --> [unknown packet] 0x1E Packet
#     472 --> [unknown packet] 0x4C Packet
#    1029 --> [unknown packet] 0x27 Packet   - No

    packet_name = 'unknown'

    class Record(Vector, Type):
        __slots__ = ()

        @classmethod
        def read(cls, file_object):
            return cls(*(Byte.read(file_object) for i in range(3)))

        @classmethod
        def send(cls, record, socket):
            for coord in record:
                Byte.send(coord, socket)

    @staticmethod
    def get_definition(context):
        return [
            {'entity_id': VarInt},
            {'y': Angle},
            {'z': Short}
            # {'player_motion_x': VarInt},
            # {'player_motion_y': Float},
            # {'player_motion_z': Float},
        ]

    # Access the 'x', 'y', 'z' fields as a Vector tuple.
    position = multi_attribute_alias(Vector, 'x', 'y', 'z')

    # Access the 'player_motion_{x,y,z}' fields as a Vector tuple.
    player_motion = multi_attribute_alias(
        Vector, 'player_motion_x', 'player_motion_y', 'player_motion_z')

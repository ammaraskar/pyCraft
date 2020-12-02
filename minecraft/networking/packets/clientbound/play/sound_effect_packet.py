from minecraft.networking.packets import Packet
from minecraft.networking.types import (
    VarInt, String, Float, Byte, Type, Integer, Vector, Enum,
)

__all__ = 'SoundEffectPacket',


class SoundEffectPacket(Packet):
    @staticmethod
    def get_id(context):
        return 0x51 if context.protocol_later_eq(721) else \
               0x52 if context.protocol_later_eq(550) else \
               0x51 if context.protocol_later_eq(471) else \
               0x4D if context.protocol_later_eq(461) else \
               0x4E if context.protocol_later_eq(451) else \
               0x4D if context.protocol_later_eq(389) else \
               0x4C if context.protocol_later_eq(352) else \
               0x4B if context.protocol_later_eq(345) else \
               0x4A if context.protocol_later_eq(343) else \
               0x49 if context.protocol_later_eq(336) else \
               0x48 if context.protocol_later_eq(318) else \
               0x46 if context.protocol_later_eq(110) else \
               0x47

    packet_name = 'sound effect'

    @staticmethod
    def get_definition(context):
        return [
            ({'sound_category': VarInt}
                if context.protocol_later_eq(321)
                and context.protocol_earlier(326) else {}),
            {'sound_id': VarInt},
            ({'sound_category': VarInt}
                if context.protocol_later_eq(95)
                and context.protocol_earlier(321)
                or context.protocol_later_eq(326) else {}),
            ({'parroted_entity_type': String}
                if context.protocol_later_eq(321)
                and context.protocol_earlier(326) else {}),
            {'effect_position': SoundEffectPacket.EffectPosition},
            {'volume': Float},
            {'pitch': SoundEffectPacket.Pitch},
        ]

    class SoundCategory(Enum):
        MASTER = 0
        MUSIC = 1
        RECORDS = 2
        WEATHER = 3
        BLOCKS = 4
        HOSTILE = 5
        NEUTRAL = 6
        PLAYERS = 7
        AMBIENT = 8
        VOICE = 9

    class EffectPosition(Type):
        @classmethod
        def read(cls, file_object):
            return Vector(*(Integer.read(file_object) / 8.0 for i in range(3)))

        @classmethod
        def send(cls, value, socket):
            for coordinate in value:
                Integer.send(int(coordinate * 8), socket)

    class Pitch(Type):
        @staticmethod
        def read_with_context(file_object, context):
            if context.protocol_later_eq(201):
                value = Float.read(file_object)
            else:
                value = Byte.read(file_object)
            if context.protocol_earlier(204):
                value /= 63.5
            return value

        @staticmethod
        def send_with_context(value, socket, context):
            if context.protocol_earlier(204):
                value *= 63.5
            if context.protocol_later_eq(201):
                Float.send(value, socket)
            else:
                Byte.send(int(value), socket)

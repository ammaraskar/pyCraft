from minecraft.networking.packets import Packet
from minecraft.networking.types import (
    String, Byte, VarInt, Boolean, UnsignedByte, Enum, BitFieldEnum,
    AbsoluteHand
)


class ClientSettingsPacket(Packet):
    @staticmethod
    def get_id(context):
        return 0x05 if context.protocol_version >= 464 else \
               0x04 if context.protocol_version >= 389 else \
               0x03 if context.protocol_version >= 343 else \
               0x04 if context.protocol_version >= 336 else \
               0x05 if context.protocol_version >= 318 else \
               0x04 if context.protocol_version >= 94 else \
               0x15

    packet_name = 'client settings'

    get_definition = staticmethod(lambda context: [
        {'locale': String},
        {'view_distance': Byte},
        {'chat_mode': VarInt if context.protocol_version > 47 else Byte},
        {'chat_colors': Boolean},
        {'displayed_skin_parts': UnsignedByte},
        {'main_hand': VarInt} if context.protocol_version > 49 else {}])

    field_enum = classmethod(
        lambda cls, field, context: {
            'chat_mode': cls.ChatMode,
            'displayed_skin_parts': cls.SkinParts,
            'main_hand': AbsoluteHand,
        }.get(field))

    class ChatMode(Enum):
        FULL = 0    # Receive all types of chat messages.
        SYSTEM = 1  # Receive only command results and game information.
        NONE = 2    # Receive only game information.

    class SkinParts(BitFieldEnum):
        CAPE = 0x01
        JACKET = 0x02
        LEFT_SLEEVE = 0x04
        RIGHT_SLEEVE = 0x08
        LEFT_PANTS_LEG = 0x10
        RIGHT_PANTS_LEG = 0x20
        HAT = 0x40

        ALL = 0x7F
        NONE = 0x00

    # This class alias is retained for backward compatibility.
    Hand = AbsoluteHand

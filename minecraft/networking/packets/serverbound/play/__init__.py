from minecraft.networking.packets import (
    Packet, AbstractKeepAlivePacket, AbstractPluginMessagePacket
)

from minecraft.networking.types import (
    Double, Float, Boolean, VarInt, String, Enum
)

from .client_settings_packet import ClientSettingsPacket


# Formerly known as state_playing_serverbound.
def get_packets(context):
    packets = {
        KeepAlivePacket,
        ChatPacket,
        PositionAndLookPacket,
        AnimationPacket,
        ClientStatusPacket,
        ClientSettingsPacket,
        PluginMessagePacket,
    }
    if context.protocol_version >= 107:
        packets |= {
            TeleportConfirmPacket,
        }
    return packets


class KeepAlivePacket(AbstractKeepAlivePacket):
    @staticmethod
    def get_id(context):
        return 0x0B if context.protocol_version >= 345 else \
               0x0A if context.protocol_version >= 343 else \
               0x0B if context.protocol_version >= 336 else \
               0x0C if context.protocol_version >= 318 else \
               0x0B if context.protocol_version >= 107 else \
               0x00


class ChatPacket(Packet):
    @staticmethod
    def get_id(context):
        return 0x01 if context.protocol_version >= 343 else \
               0x02 if context.protocol_version >= 336 else \
               0x03 if context.protocol_version >= 318 else \
               0x02 if context.protocol_version >= 107 else \
               0x01

    @staticmethod
    def get_max_length(context):
        return 256 if context.protocol_version >= 306 else \
               100

    @property
    def max_length(self):
        if self.context is not None:
            return self.get_max_length(self.context)

    packet_name = "chat"
    definition = [
        {'message': String}]


class PositionAndLookPacket(Packet):
    @staticmethod
    def get_id(context):
        return 0x0E if context.protocol_version >= 345 else \
               0x0D if context.protocol_version >= 343 else \
               0x0E if context.protocol_version >= 336 else \
               0x0F if context.protocol_version >= 332 else \
               0x0E if context.protocol_version >= 318 else \
               0x0D if context.protocol_version >= 107 else \
               0x06

    packet_name = "position and look"
    definition = [
        {'x': Double},
        {'feet_y': Double},
        {'z': Double},
        {'yaw': Float},
        {'pitch': Float},
        {'on_ground': Boolean}]


class TeleportConfirmPacket(Packet):
    # Note: added between protocol versions 47 and 107.
    id = 0x00
    packet_name = "teleport confirm"
    definition = [
        {'teleport_id': VarInt}]


class AnimationPacket(Packet, Enum):
    @staticmethod
    def get_id(context):
        return 0x1D if context.protocol_version >= 345 else \
               0x1C if context.protocol_version >= 343 else \
               0x1D if context.protocol_version >= 332 else \
               0x1C if context.protocol_version >= 318 else \
               0x1A if context.protocol_version >= 107 else \
               0x0A

    packet_name = "animation"
    get_definition = staticmethod(lambda context: [
        {'hand': VarInt} if context.protocol_version >= 107 else {}])
    field_enum = classmethod(
        lambda cls, field: cls if field == 'hand' else None)

    HAND_MAIN = 0
    HAND_OFF = 1


class ClientStatusPacket(Packet, Enum):
    @staticmethod
    def get_id(context):
        return 0x02 if context.protocol_version >= 343 else \
               0x03 if context.protocol_version >= 336 else \
               0x04 if context.protocol_version >= 318 else \
               0x03 if context.protocol_version >= 80 else \
               0x02 if context.protocol_version >= 67 else \
               0x17 if context.protocol_version >= 49 else \
               0x16

    packet_name = "client status"
    get_definition = staticmethod(lambda context: [
        {'action_id': VarInt}])
    field_enum = classmethod(
        lambda cls, field: cls if field == 'action_id' else None)

    RESPAWN = 0
    REQUEST_STATS = 1
    # Note: Open Inventory (id 2) was removed in protocol version 319
    OPEN_INVENTORY = 2


class PluginMessagePacket(AbstractPluginMessagePacket):
    @staticmethod
    def get_id(context):
        return 0x09 if context.protocol_version >= 345 else \
               0x08 if context.protocol_version >= 343 else \
               0x09 if context.protocol_version >= 336 else \
               0x0A if context.protocol_version >= 317 else \
               0x09 if context.protocol_version >= 94 else \
               0x17

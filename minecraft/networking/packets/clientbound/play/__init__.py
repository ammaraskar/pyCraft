from minecraft.networking.packets import (
    Packet, AbstractKeepAlivePacket, AbstractPluginMessagePacket
)

from minecraft.networking.types import (
    Integer, FixedPointInteger, UnsignedByte, Byte, Boolean, UUID, Short,
    VarInt, Double, Float, String, Enum,
)

from .combat_event_packet import CombatEventPacket
from .map_packet import MapPacket
from .player_list_item_packet import PlayerListItemPacket
from .player_position_and_look_packet import PlayerPositionAndLookPacket
from .spawn_object_packet import SpawnObjectPacket
from .block_change_packet import BlockChangePacket, MultiBlockChangePacket
from .explosion_packet import ExplosionPacket


# Formerly known as state_playing_clientbound.
def get_packets(context):
    packets = {
        KeepAlivePacket,
        JoinGamePacket,
        ChatMessagePacket,
        PlayerPositionAndLookPacket,
        MapPacket,
        PlayerListItemPacket,
        DisconnectPacket,
        SpawnPlayerPacket,
        EntityVelocityPacket,
        UpdateHealthPacket,
        CombatEventPacket,
        ExplosionPacket,
        SpawnObjectPacket,
        BlockChangePacket,
        MultiBlockChangePacket,
        PluginMessagePacket,
        PlayerListHeaderAndFooterPacket,
    }
    if context.protocol_version <= 47:
        packets |= {
            SetCompressionPacket,
        }
    return packets


class KeepAlivePacket(AbstractKeepAlivePacket):
    @staticmethod
    def get_id(context):
        return 0x20 if context.protocol_version >= 477 else \
               0x21 if context.protocol_version >= 389 else \
               0x20 if context.protocol_version >= 345 else \
               0x1F if context.protocol_version >= 332 else \
               0x20 if context.protocol_version >= 318 else \
               0x1F if context.protocol_version >= 107 else \
               0x00


class JoinGamePacket(Packet):
    @staticmethod
    def get_id(context):
        return 0x25 if context.protocol_version >= 389 else \
               0x24 if context.protocol_version >= 345 else \
               0x23 if context.protocol_version >= 332 else \
               0x24 if context.protocol_version >= 318 else \
               0x23 if context.protocol_version >= 107 else \
               0x01

    packet_name = "join game"
    get_definition = staticmethod(lambda context: list(filter(None.__ne__, [
        {'entity_id': Integer},
        {'game_mode': UnsignedByte},
        {'dimension': Integer if context.protocol_version >= 108 else Byte},
        {'difficulty': UnsignedByte} if context.protocol_version < 477 else None,
        {'max_players': UnsignedByte},
        {'level_type': String},
        {'view_distance': VarInt} if context.protocol_version >= 477 else None,
        {'reduced_debug_info': Boolean}])))


class ChatMessagePacket(Packet):
    @staticmethod
    def get_id(context):
        return 0x0E if context.protocol_version >= 343 else \
               0x0F if context.protocol_version >= 332 else \
               0x10 if context.protocol_version >= 317 else \
               0x0F if context.protocol_version >= 107 else \
               0x02

    packet_name = "chat message"
    definition = [
        {'json_data': String},
        {'position': Byte}]

    class Position(Enum):
        CHAT = 0       # A player-initiated chat message.
        SYSTEM = 1     # The result of running a command.
        GAME_INFO = 2  # Displayed above the hotbar in vanilla clients.


class DisconnectPacket(Packet):
    @staticmethod
    def get_id(context):
        return 0x1A if context.protocol_version >= 477 else \
               0x1B if context.protocol_version >= 345 else \
               0x1A if context.protocol_version >= 332 else \
               0x1B if context.protocol_version >= 318 else \
               0x1A if context.protocol_version >= 107 else \
               0x40

    packet_name = "disconnect"

    definition = [
        {'json_data': String}]


class SetCompressionPacket(Packet):
    # Note: removed between protocol versions 47 and 107.
    id = 0x46
    packet_name = "set compression"
    definition = [
        {'threshold': VarInt}]


class SpawnPlayerPacket(Packet):
    @staticmethod
    def get_id(context):
        return 0x05 if context.protocol_version >= 67 else \
               0x0C

    packet_name = 'spawn player'
    get_definition = staticmethod(lambda context: [
        {'entity_id': VarInt},
        {'player_UUID': UUID},
        {'x': Double} if context.protocol_version >= 100
        else {'x': FixedPointInteger},
        {'y': Double} if context.protocol_version >= 100
        else {'y': FixedPointInteger},
        {'z': Double} if context.protocol_version >= 100
        else {'z': FixedPointInteger},
        {'yaw': Float},
        {'pitch': Float},
        # TODO: read entity metadata
        {'current_item': Short} if context.protocol_version <= 49 else {}
    ])


class EntityVelocityPacket(Packet):
    @staticmethod
    def get_id(context):
        return 0x45 if context.protocol_version >= 477 else \
               0x41 if context.protocol_version >= 389 else \
               0x40 if context.protocol_version >= 352 else \
               0x3F if context.protocol_version >= 345 else \
               0x3E if context.protocol_version >= 336 else \
               0x3D if context.protocol_version >= 332 else \
               0x3B if context.protocol_version >= 86 else \
               0x3C if context.protocol_version >= 77 else \
               0x3B if context.protocol_version >= 67 else \
               0x12

    packet_name = 'entity velocity'
    get_definition = staticmethod(lambda context: [
        {'entity_id': VarInt},
        {'velocity_x': Short},
        {'velocity_y': Short},
        {'velocity_z': Short}
    ])


class UpdateHealthPacket(Packet):
    @staticmethod
    def get_id(context):
        return 0x48 if context.protocol_version >= 477 else \
               0x44 if context.protocol_version >= 389 else \
               0x43 if context.protocol_version >= 352 else \
               0x42 if context.protocol_version >= 345 else \
               0x41 if context.protocol_version >= 336 else \
               0x40 if context.protocol_version >= 318 else \
               0x3E if context.protocol_version >= 86 else \
               0x3F if context.protocol_version >= 77 else \
               0x3E if context.protocol_version >= 67 else \
               0x06

    packet_name = 'update health'
    get_definition = staticmethod(lambda context: [
        {'health': Float},
        {'food': VarInt},
        {'food_saturation': Float}
    ])


class PluginMessagePacket(AbstractPluginMessagePacket):
    @staticmethod
    def get_id(context):
        return 0x18 if context.protocol_version >= 477 else \
               0x19 if context.protocol_version >= 345 else \
               0x18 if context.protocol_version >= 332 else \
               0x19 if context.protocol_version >= 318 else \
               0x18 if context.protocol_version >= 70 else \
               0x3F


class PlayerListHeaderAndFooterPacket(Packet):
    @staticmethod
    def get_id(context):
        return 0x53 if context.protocol_version >= 477 else \
               0x4E if context.protocol_version >= 393 else \
               0x4A if context.protocol_version >= 338 else \
               0x49 if context.protocol_version >= 335 else \
               0x47 if context.protocol_version >= 110 else \
               0x48 if context.protocol_version >= 107 else \
               0x47

    packet_name = 'player list header and footer'
    definition = [
        {'header': String},
        {'footer': String}]

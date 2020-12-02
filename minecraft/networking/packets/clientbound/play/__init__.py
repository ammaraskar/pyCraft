from minecraft.networking.packets import (
    Packet, AbstractKeepAlivePacket, AbstractPluginMessagePacket
)

from minecraft.networking.types import (
    FixedPoint, Integer, Angle, UnsignedByte, Byte, Boolean, UUID, Short,
    VarInt, Double, Float, String, Enum, Difficulty, Long, Vector, Direction,
    PositionAndLook, multi_attribute_alias, attribute_transform,
)

from .combat_event_packet import CombatEventPacket
from .map_packet import MapPacket
from .player_list_item_packet import PlayerListItemPacket
from .player_position_and_look_packet import PlayerPositionAndLookPacket
from .spawn_object_packet import SpawnObjectPacket
from .block_change_packet import BlockChangePacket, MultiBlockChangePacket
from .explosion_packet import ExplosionPacket
from .sound_effect_packet import SoundEffectPacket
from .face_player_packet import FacePlayerPacket
from .join_game_and_respawn_packets import JoinGamePacket, RespawnPacket


# Formerly known as state_playing_clientbound.
def get_packets(context):
    packets = {
        KeepAlivePacket,
        JoinGamePacket,
        ServerDifficultyPacket,
        ChatMessagePacket,
        PlayerPositionAndLookPacket,
        MapPacket,
        PlayerListItemPacket,
        DisconnectPacket,
        SpawnPlayerPacket,
        EntityVelocityPacket,
        EntityPositionDeltaPacket,
        TimeUpdatePacket,
        UpdateHealthPacket,
        CombatEventPacket,
        ExplosionPacket,
        SpawnObjectPacket,
        BlockChangePacket,
        MultiBlockChangePacket,
        RespawnPacket,
        PluginMessagePacket,
        PlayerListHeaderAndFooterPacket,
        EntityLookPacket
    }
    if context.protocol_earlier_eq(47):
        packets |= {
            SetCompressionPacket,
        }
    if context.protocol_later_eq(94):
        packets |= {
            SoundEffectPacket,
        }
    if context.protocol_later_eq(352):
        packets |= {
            FacePlayerPacket
        }
    return packets


class KeepAlivePacket(AbstractKeepAlivePacket):
    @staticmethod
    def get_id(context):
        return 0x1F if context.protocol_later_eq(741) else \
               0x20 if context.protocol_later_eq(721) else \
               0x21 if context.protocol_later_eq(550) else \
               0x20 if context.protocol_later_eq(471) else \
               0x21 if context.protocol_later_eq(389) else \
               0x20 if context.protocol_later_eq(345) else \
               0x1F if context.protocol_later_eq(332) else \
               0x20 if context.protocol_later_eq(318) else \
               0x1F if context.protocol_later_eq(107) else \
               0x00


class ServerDifficultyPacket(Packet):
    @staticmethod
    def get_id(context):
        return 0x0D if context.protocol_later_eq(721) else \
               0x0E if context.protocol_later_eq(550) else \
               0x0D if context.protocol_later_eq(332) else \
               0x0E if context.protocol_later_eq(318) else \
               0x0D if context.protocol_later_eq(70) else \
               0x41

    packet_name = 'server difficulty'
    get_definition = staticmethod(lambda context: [
        {'difficulty': UnsignedByte},
        {'is_locked': Boolean} if context.protocol_later_eq(464) else {},
    ])

    # These aliases declare the Enum type corresponding to each field:
    Difficulty = Difficulty


class ChatMessagePacket(Packet):
    @staticmethod
    def get_id(context):
        return 0x0E if context.protocol_later_eq(721) else \
               0x0F if context.protocol_later_eq(550) else \
               0x0E if context.protocol_later_eq(343) else \
               0x0F if context.protocol_later_eq(332) else \
               0x10 if context.protocol_later_eq(317) else \
               0x0F if context.protocol_later_eq(107) else \
               0x02

    packet_name = "chat message"
    get_definition = staticmethod(lambda context: [
        {'json_data': String},
        {'position': Byte},
        {'sender': UUID} if context.protocol_later_eq(718) else {},
    ])

    class Position(Enum):
        CHAT = 0       # A player-initiated chat message.
        SYSTEM = 1     # The result of running a command.
        GAME_INFO = 2  # Displayed above the hotbar in vanilla clients.


class DisconnectPacket(Packet):
    @staticmethod
    def get_id(context):
        return 0x19 if context.protocol_later_eq(741) else \
               0x1A if context.protocol_later_eq(721) else \
               0x1B if context.protocol_later_eq(550) else \
               0x1A if context.protocol_later_eq(471) else \
               0x1B if context.protocol_later_eq(345) else \
               0x1A if context.protocol_later_eq(332) else \
               0x1B if context.protocol_later_eq(318) else \
               0x1A if context.protocol_later_eq(107) else \
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
        return 0x04 if context.protocol_later_eq(721) else \
               0x05 if context.protocol_later_eq(67) else \
               0x0C

    packet_name = 'spawn player'
    get_definition = staticmethod(lambda context: [
        {'entity_id': VarInt},
        {'player_UUID': UUID},
        {'x': Double} if context.protocol_later_eq(100)
        else {'x': FixedPoint(Integer)},
        {'y': Double} if context.protocol_later_eq(100)
        else {'y': FixedPoint(Integer)},
        {'z': Double} if context.protocol_later_eq(100)
        else {'z': FixedPoint(Integer)},
        {'yaw': Angle},
        {'pitch': Angle},
        {'current_item': Short} if context.protocol_earlier_eq(49) else {},
        # TODO: read entity metadata (protocol < 550)
    ])

    # Access the 'x', 'y', 'z' fields as a Vector tuple.
    position = multi_attribute_alias(Vector, 'x', 'y', 'z')

    # Access the 'yaw', 'pitch' fields as a Direction tuple.
    look = multi_attribute_alias(Direction, 'yaw', 'pitch')

    # Access the 'x', 'y', 'z', 'yaw', 'pitch' fields as a PositionAndLook.
    # NOTE: modifying the object retrieved from this property will not change
    # the packet; it can only be changed by attribute or property assignment.
    position_and_look = multi_attribute_alias(
        PositionAndLook, 'x', 'y', 'z', 'yaw', 'pitch')


class EntityVelocityPacket(Packet):
    @staticmethod
    def get_id(context):
        return 0x46 if context.protocol_later_eq(721) else \
               0x47 if context.protocol_later_eq(707) else \
               0x46 if context.protocol_later_eq(550) else \
               0x45 if context.protocol_later_eq(471) else \
               0x41 if context.protocol_later_eq(461) else \
               0x42 if context.protocol_later_eq(451) else \
               0x41 if context.protocol_later_eq(389) else \
               0x40 if context.protocol_later_eq(352) else \
               0x3F if context.protocol_later_eq(345) else \
               0x3E if context.protocol_later_eq(336) else \
               0x3D if context.protocol_later_eq(332) else \
               0x3B if context.protocol_later_eq(86) else \
               0x3C if context.protocol_later_eq(77) else \
               0x3B if context.protocol_later_eq(67) else \
               0x12

    packet_name = 'entity velocity'
    get_definition = staticmethod(lambda context: [
        {'entity_id': VarInt},
        {'velocity_x': Short},
        {'velocity_y': Short},
        {'velocity_z': Short}
    ])


class EntityPositionDeltaPacket(Packet):
    @staticmethod
    def get_id(context):
        return 0x27 if context.protocol_later_eq(741) else \
               0x28 if context.protocol_later_eq(721) else \
               0x29 if context.protocol_later_eq(550) else \
               0x28 if context.protocol_later_eq(389) else \
               0x27 if context.protocol_later_eq(345) else \
               0x26 if context.protocol_later_eq(318) else \
               0x25 if context.protocol_later_eq(94) else \
               0x26 if context.protocol_later_eq(70) else \
               0x15

    packet_name = "entity position delta"

    @staticmethod
    def get_definition(context):
        delta_type = FixedPoint(Short, 12) \
                     if context.protocol_later_eq(106) else \
                     FixedPoint(Byte)
        return [
            {'entity_id': VarInt},
            {'delta_x_float': delta_type},
            {'delta_y_float': delta_type},
            {'delta_z_float': delta_type},
            {'on_ground': Boolean},
        ]

    # The following transforms are retained for backward compatibility;
    # they represent the delta values as fixed-point integers with 12 bits
    # of fractional part, regardless of the protocol version.
    delta_x = attribute_transform(
                'delta_x_float', lambda x: int(x * 4096), lambda x: x / 4096)
    delta_y = attribute_transform(
                'delta_y_float', lambda y: int(y * 4096), lambda y: y / 4096)
    delta_z = attribute_transform(
                'delta_z_float', lambda z: int(z * 4096), lambda z: z / 4096)


class TimeUpdatePacket(Packet):
    @staticmethod
    def get_id(context):
        return 0x4E if context.protocol_later_eq(721) else \
               0x4F if context.protocol_later_eq(550) else \
               0x4E if context.protocol_later_eq(471) else \
               0x4A if context.protocol_later_eq(461) else \
               0x4B if context.protocol_later_eq(451) else \
               0x4A if context.protocol_later_eq(389) else \
               0x49 if context.protocol_later_eq(352) else \
               0x48 if context.protocol_later_eq(345) else \
               0x47 if context.protocol_later_eq(336) else \
               0x46 if context.protocol_later_eq(318) else \
               0x44 if context.protocol_later_eq(94) else \
               0x43 if context.protocol_later_eq(70) else \
               0x03

    packet_name = "time update"
    get_definition = staticmethod(lambda context: [
        {'world_age': Long},
        {'time_of_day': Long},
    ])


class UpdateHealthPacket(Packet):
    @staticmethod
    def get_id(context):
        return 0x49 if context.protocol_later_eq(721) else \
               0x4A if context.protocol_later_eq(707) else \
               0x49 if context.protocol_later_eq(550) else \
               0x48 if context.protocol_later_eq(471) else \
               0x44 if context.protocol_later_eq(461) else \
               0x45 if context.protocol_later_eq(451) else \
               0x44 if context.protocol_later_eq(389) else \
               0x43 if context.protocol_later_eq(352) else \
               0x42 if context.protocol_later_eq(345) else \
               0x41 if context.protocol_later_eq(336) else \
               0x40 if context.protocol_later_eq(318) else \
               0x3E if context.protocol_later_eq(86) else \
               0x3F if context.protocol_later_eq(77) else \
               0x3E if context.protocol_later_eq(67) else \
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
        return 0x17 if context.protocol_later_eq(741) else \
               0x18 if context.protocol_later_eq(721) else \
               0x19 if context.protocol_later_eq(550) else \
               0x18 if context.protocol_later_eq(471) else \
               0x19 if context.protocol_later_eq(345) else \
               0x18 if context.protocol_later_eq(332) else \
               0x19 if context.protocol_later_eq(318) else \
               0x18 if context.protocol_later_eq(70) else \
               0x3F


class PlayerListHeaderAndFooterPacket(Packet):
    @staticmethod
    def get_id(context):
        return 0x53 if context.protocol_later_eq(721) else \
               0x54 if context.protocol_later_eq(550) else \
               0x53 if context.protocol_later_eq(471) else \
               0x5F if context.protocol_later_eq(461) else \
               0x50 if context.protocol_later_eq(451) else \
               0x4F if context.protocol_later_eq(441) else \
               0x4E if context.protocol_later_eq(393) else \
               0x4A if context.protocol_later_eq(338) else \
               0x49 if context.protocol_later_eq(335) else \
               0x47 if context.protocol_later_eq(110) else \
               0x48 if context.protocol_later_eq(107) else \
               0x47

    packet_name = 'player list header and footer'
    definition = [
        {'header': String},
        {'footer': String}]


class EntityLookPacket(Packet):
    @staticmethod
    def get_id(context):
        return 0x29 if context.protocol_later_eq(741) else \
               0x2A if context.protocol_later_eq(721) else \
               0x2B if context.protocol_later_eq(550) else \
               0x2A if context.protocol_later_eq(389) else \
               0x29 if context.protocol_later_eq(345) else \
               0x28 if context.protocol_later_eq(318) else \
               0x27 if context.protocol_later_eq(94) else \
               0x28 if context.protocol_later_eq(70) else \
               0x16

    packet_name = 'entity look'
    definition = [
        {'entity_id': VarInt},
        {'yaw': Angle},
        {'pitch': Angle},
        {'on_ground': Boolean}
    ]

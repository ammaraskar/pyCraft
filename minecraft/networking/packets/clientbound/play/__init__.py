from minecraft.networking.packets import (
    Packet, PacketBuffer, AbstractKeepAlivePacket, AbstractPluginMessagePacket
)

from minecraft.networking.types import (
    Integer, UnsignedByte, Byte, Boolean, UUID, Short, Position,
    VarInt, Double, Float, String, Enum,
)

from .combat_event_packet import CombatEventPacket
from .map_packet import MapPacket
from .player_list_item_packet import PlayerListItemPacket
from .player_position_and_look_packet import PlayerPositionAndLookPacket
from .spawn_object_packet import SpawnObjectPacket


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
    }
    if context.protocol_version <= 47:
        packets |= {
            SetCompressionPacket,
        }
    return packets


class KeepAlivePacket(AbstractKeepAlivePacket):
    @staticmethod
    def get_id(context):
        return 0x1F if context.protocol_version >= 332 else \
               0x20 if context.protocol_version >= 318 else \
               0x1F if context.protocol_version >= 107 else \
               0x00


class JoinGamePacket(Packet):
    @staticmethod
    def get_id(context):
        return 0x23 if context.protocol_version >= 332 else \
               0x24 if context.protocol_version >= 318 else \
               0x23 if context.protocol_version >= 107 else \
               0x01

    packet_name = "join game"
    get_definition = staticmethod(lambda context: [
        {'entity_id': Integer},
        {'game_mode': UnsignedByte},
        {'dimension': Integer if context.protocol_version >= 108 else Byte},
        {'difficulty': UnsignedByte},
        {'max_players': UnsignedByte},
        {'level_type': String},
        {'reduced_debug_info': Boolean}])


class ChatMessagePacket(Packet):
    @staticmethod
    def get_id(context):
        return 0x0F if context.protocol_version >= 332 else \
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
        return 0x1A if context.protocol_version >= 332 else \
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
        {'x': Double} if context.protocol_version >= 100 else {'x': Integer},
        {'y': Double} if context.protocol_version >= 100 else {'y': Integer},
        {'z': Double} if context.protocol_version >= 100 else {'z': Integer},
        {'yaw': Float},
        {'pitch': Float},
        # TODO: read entity metadata
        {'current_item': Short} if context.protocol_version <= 49 else {}
    ])


class EntityVelocityPacket(Packet):
    @staticmethod
    def get_id(context):
        return 0x3E if context.protocol_version >= 336 else \
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
        return 0x41 if context.protocol_version >= 336 else \
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


class ExplosionPacket(Packet):
    @staticmethod
    def get_id(context):
        return 0x1C if context.protocol_version >= 332 else \
               0x1D if context.protocol_version >= 318 else \
               0x1C if context.protocol_version >= 80 else \
               0x1B if context.protocol_version >= 67 else \
               0x27

    packet_name = 'explosion'

    class Record(Position):
        pass

    def read(self, file_object):
        self.x = Float.read(file_object)
        self.y = Float.read(file_object)
        self.z = Float.read(file_object)
        self.radius = Float.read(file_object)
        records_count = VarInt.read(file_object)
        self.records = []
        for i in range(records_count):
            rec_x = Byte.read(file_object)
            rec_y = Byte.read(file_object)
            rec_z = Byte.read(file_object)
            record = ExplosionPacket.Record(rec_x, rec_y, rec_z)
            self.records.append(record)
        self.player_motion_x = Float.read(file_object)
        self.player_motion_y = Float.read(file_object)
        self.player_motion_z = Float.read(file_object)

    def write(self, socket, compression_threshold=None):
        raise NotImplementedError


class BlockChangePacket(Packet):
    @staticmethod
    def get_id(context):
        return 0x0B if context.protocol_version >= 332 else \
               0x0C if context.protocol_version >= 318 else \
               0x0B if context.protocol_version >= 67 else \
               0x24 if context.protocol_version >= 62 else \
               0x23

    packet_name = 'block change'

    def read(self, file_object):
        self.location = Position.read(file_object)
        blockData = VarInt.read(file_object)
        self.blockId = (blockData >> 4)
        self.blockMeta = (blockData & 0xF)

    def write(self, socket, compression_threshold=None):
        packet_buffer = PacketBuffer()
        (x, y, z) = self.location
        Position.send(x, y, z, packet_buffer)
        blockData = ((self.blockId << 4) | (self.blockMeta & 0xF))
        VarInt.send(blockData)
        self._write_buffer(socket, packet_buffer, compression_threshold)


class MultiBlockChangePacket(Packet):
    @staticmethod
    def get_id(context):
        return 0x10 if context.protocol_version >= 332 else \
               0x11 if context.protocol_version >= 318 else \
               0x10 if context.protocol_version >= 67 else \
               0x22

    packet_name = 'multi block change'

    class Record(object):
        __slots__ = 'x', 'y', 'z', 'blockId', 'blockMeta'

        def __init__(self, horizontal_position, y_coordinate, blockData):
            self.x = (horizontal_position & 0xF0) >> 4
            self.y = y_coordinate
            self.z = (horizontal_position & 0x0F)
            self.blockId = (blockData >> 4)
            self.blockMeta = (blockData & 0xF)

        def __repr__(self):
            return ('Record(x=%s, y=%s, z=%s, blockId=%s)'
                    % (self.x, self.y, self.z, self.blockId))

        def __str__(self):
            return self.__repr__()

    def read(self, file_object):
        self.chunk_x = Integer.read(file_object)
        self.chunk_z = Integer.read(file_object)
        records_count = VarInt.read(file_object)
        self.records = []
        for i in range(records_count):
            rec_horizontal_position = UnsignedByte.read(file_object)
            rec_y_coordinate = UnsignedByte.read(file_object)
            rec_blockData = VarInt.read(file_object)
            record = MultiBlockChangePacket.Record(
                         rec_horizontal_position,
                         rec_y_coordinate, rec_blockData)
            self.records.append(record)

    def write(self, socket, compression_threshold=None):
        raise NotImplementedError


class PluginMessagePacket(AbstractPluginMessagePacket):
    @staticmethod
    def get_id(context):
        return 0x18 if context.protocol_version >= 332 else \
               0x19 if context.protocol_version >= 318 else \
               0x18 if context.protocol_version >= 70 else \
               0x3F

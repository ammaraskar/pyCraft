from minecraft.networking.packets import (
    Packet, AbstractKeepAlivePacket, AbstractPluginMessagePacket
)

from minecraft.networking.types import (
    Double, Float, Boolean, VarInt, String, Byte, Position, Enum,
    RelativeHand, BlockFace, Vector, Direction, PositionAndLook,
    multi_attribute_alias
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
        PlayerBlockPlacementPacket,
    }
    if context.protocol_version >= 69:
        packets |= {
            UseItemPacket,
        }
    if context.protocol_version >= 107:
        packets |= {
            TeleportConfirmPacket,
        }
    return packets


class KeepAlivePacket(AbstractKeepAlivePacket):
    @staticmethod
    def get_id(context):
        return 0x0F if context.protocol_version >= 471 else \
               0x10 if context.protocol_version >= 464 else \
               0x0E if context.protocol_version >= 389 else \
               0x0C if context.protocol_version >= 386 else \
               0x0B if context.protocol_version >= 345 else \
               0x0A if context.protocol_version >= 343 else \
               0x0B if context.protocol_version >= 336 else \
               0x0C if context.protocol_version >= 318 else \
               0x0B if context.protocol_version >= 107 else \
               0x00


class ChatPacket(Packet):
    @staticmethod
    def get_id(context):
        return 0x03 if context.protocol_version >= 464 else \
               0x02 if context.protocol_version >= 389 else \
               0x01 if context.protocol_version >= 343 else \
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
        return 0x12 if context.protocol_version >= 471 else \
               0x13 if context.protocol_version >= 464 else \
               0x11 if context.protocol_version >= 389 else \
               0x0F if context.protocol_version >= 386 else \
               0x0E if context.protocol_version >= 345 else \
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

    # Access the 'x', 'feet_y', 'z' fields as a Vector tuple.
    position = multi_attribute_alias(Vector, 'x', 'feet_y', 'z')

    # Access the 'yaw', 'pitch' fields as a Direction tuple.
    look = multi_attribute_alias(Direction, 'yaw', 'pitch')

    # Access the 'x', 'feet_y', 'z', 'yaw', 'pitch' fields as a
    # PositionAndLook.
    # NOTE: modifying the object retrieved from this property will not change
    # the packet; it can only be changed by attribute or property assignment.
    position_and_look = multi_attribute_alias(
        PositionAndLook, 'x', 'feet_y', 'z', 'yaw', 'pitch')


class TeleportConfirmPacket(Packet):
    # Note: added between protocol versions 47 and 107.
    id = 0x00
    packet_name = "teleport confirm"
    definition = [
        {'teleport_id': VarInt}]


class AnimationPacket(Packet):
    @staticmethod
    def get_id(context):
        return 0x2A if context.protocol_version >= 468 else \
               0x29 if context.protocol_version >= 464 else \
               0x27 if context.protocol_version >= 389 else \
               0x25 if context.protocol_version >= 386 else \
               0x1D if context.protocol_version >= 345 else \
               0x1C if context.protocol_version >= 343 else \
               0x1D if context.protocol_version >= 332 else \
               0x1C if context.protocol_version >= 318 else \
               0x1A if context.protocol_version >= 107 else \
               0x0A

    packet_name = "animation"
    get_definition = staticmethod(lambda context: [
        {'hand': VarInt} if context.protocol_version >= 107 else {}])

    Hand = RelativeHand
    HAND_MAIN, HAND_OFF = Hand.MAIN, Hand.OFF  # For backward compatibility.


class ClientStatusPacket(Packet, Enum):
    @staticmethod
    def get_id(context):
        return 0x04 if context.protocol_version >= 464 else \
               0x03 if context.protocol_version >= 389 else \
               0x02 if context.protocol_version >= 343 else \
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
        lambda cls, field, context: cls if field == 'action_id' else None)

    RESPAWN = 0
    REQUEST_STATS = 1
    # Note: Open Inventory (id 2) was removed in protocol version 319
    OPEN_INVENTORY = 2


class PluginMessagePacket(AbstractPluginMessagePacket):
    @staticmethod
    def get_id(context):
        return 0x0B if context.protocol_version >= 464 else \
               0x0A if context.protocol_version >= 389 else \
               0x09 if context.protocol_version >= 345 else \
               0x08 if context.protocol_version >= 343 else \
               0x09 if context.protocol_version >= 336 else \
               0x0A if context.protocol_version >= 317 else \
               0x09 if context.protocol_version >= 94 else \
               0x17


class PlayerBlockPlacementPacket(Packet):
    """Realizaton of http://wiki.vg/Protocol#Player_Block_Placement packet
    Usage:
        packet = PlayerBlockPlacementPacket()
        packet.location = Position(x=1200, y=65, z=-420)
        packet.face = packet.Face.TOP   # See networking.types.BlockFace.
        packet.hand = packet.Hand.MAIN  # See networking.types.RelativeHand.
    Next values are called in-block coordinates.
    They are calculated using raytracing. From 0 to 1 (from Minecraft 1.11)
    or integers from 0 to 15 or, in a special case, -1 (1.10.2 and earlier).
        packet.x = 0.725
        packet.y = 0.125
        packet.z = 0.555"""

    @staticmethod
    def get_id(context):
        return 0x2C if context.protocol_version >= 468 else \
               0x2B if context.protocol_version >= 464 else \
               0x29 if context.protocol_version >= 389 else \
               0x27 if context.protocol_version >= 386 else \
               0x1F if context.protocol_version >= 345 else \
               0x1E if context.protocol_version >= 343 else \
               0x1F if context.protocol_version >= 332 else \
               0x1E if context.protocol_version >= 318 else \
               0x1C if context.protocol_version >= 94 else \
               0x08

    packet_name = 'player block placement'

    @staticmethod
    def get_definition(context):
        return [
            {'hand': VarInt} if context.protocol_version >= 453 else {},
            {'location': Position},
            {'face': VarInt if context.protocol_version >= 69 else Byte},
            {'hand': VarInt} if context.protocol_version < 453 else {},
            {'x': Float if context.protocol_version >= 309 else Byte},
            {'y': Float if context.protocol_version >= 309 else Byte},
            {'z': Float if context.protocol_version >= 309 else Byte},
            ({'inside_block': Boolean}
                if context.protocol_version >= 453 else {}),
        ]

    # PlayerBlockPlacementPacket.Hand is an alias for RelativeHand.
    Hand = RelativeHand

    # PlayerBlockPlacementPacket.Face is an alias for BlockFace.
    Face = BlockFace


class UseItemPacket(Packet):
    @staticmethod
    def get_id(context):
        return 0x2D if context.protocol_version >= 468 else \
               0x2C if context.protocol_version >= 464 else \
               0x2A if context.protocol_version >= 389 else \
               0x28 if context.protocol_version >= 386 else \
               0x20 if context.protocol_version >= 345 else \
               0x1F if context.protocol_version >= 343 else \
               0x20 if context.protocol_version >= 332 else \
               0x1F if context.protocol_version >= 318 else \
               0x1D if context.protocol_version >= 94 else \
               0x1A if context.protocol_version >= 70 else \
               0x08

    packet_name = "use item"
    get_definition = staticmethod(lambda context: [
        {'hand': VarInt}])

    Hand = RelativeHand

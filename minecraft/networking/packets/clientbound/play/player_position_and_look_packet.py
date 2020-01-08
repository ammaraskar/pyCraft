from minecraft.networking.packets import Packet

from minecraft.networking.types import (
    Double, Float, Byte, VarInt, BitFieldEnum, Vector, Direction,
    PositionAndLook, multi_attribute_alias,
)


class PlayerPositionAndLookPacket(Packet, BitFieldEnum):
    @staticmethod
    def get_id(context):
        return 0x36 if context.protocol_version >= 550 else \
               0x35 if context.protocol_version >= 471 else \
               0x33 if context.protocol_version >= 451 else \
               0x32 if context.protocol_version >= 389 else \
               0x31 if context.protocol_version >= 352 else \
               0x30 if context.protocol_version >= 345 else \
               0x2F if context.protocol_version >= 336 else \
               0x2E if context.protocol_version >= 332 else \
               0x2F if context.protocol_version >= 318 else \
               0x2E if context.protocol_version >= 70 else \
               0x08

    packet_name = "player position and look"
    get_definition = staticmethod(lambda context: [
        {'x': Double},
        {'y': Double},
        {'z': Double},
        {'yaw': Float},
        {'pitch': Float},
        {'flags': Byte},
        {'teleport_id': VarInt} if context.protocol_version >= 107 else {},
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

    field_enum = classmethod(
        lambda cls, field, context: cls if field == 'flags' else None)

    FLAG_REL_X = 0x01
    FLAG_REL_Y = 0x02
    FLAG_REL_Z = 0x04
    FLAG_REL_YAW = 0x08
    FLAG_REL_PITCH = 0x10

    # This alias is retained for backward compatibility.
    PositionAndLook = PositionAndLook

    # Update a PositionAndLook instance using this packet.
    def apply(self, target):
        # pylint: disable=no-member
        if self.flags & self.FLAG_REL_X:
            target.x += self.x
        else:
            target.x = self.x

        if self.flags & self.FLAG_REL_Y:
            target.y += self.y
        else:
            target.y = self.y

        if self.flags & self.FLAG_REL_Z:
            target.z += self.z
        else:
            target.z = self.z

        if self.flags & self.FLAG_REL_YAW:
            target.yaw += self.yaw
        else:
            target.yaw = self.yaw

        if self.flags & self.FLAG_REL_PITCH:
            target.pitch += self.pitch
        else:
            target.pitch = self.pitch

        target.yaw %= 360
        target.pitch %= 360

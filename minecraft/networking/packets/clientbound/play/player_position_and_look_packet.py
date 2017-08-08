from minecraft.networking.packets import Packet

from minecraft.networking.types import (
    Double, Float, Byte, VarInt
)


class PlayerPositionAndLookPacket(Packet):
    @staticmethod
    def get_id(context):
        return 0x2F if context.protocol_version >= 336 else \
               0x2E if context.protocol_version >= 318 else \
               0x2F if context.protocol_version >= 107 else \
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

    FLAG_REL_X = 0x01
    FLAG_REL_Y = 0x02
    FLAG_REL_Z = 0x04
    FLAG_REL_YAW = 0x08
    FLAG_REL_PITCH = 0x10

    class PositionAndLook(object):
        __slots__ = 'x', 'y', 'z', 'yaw', 'pitch'

        def __init__(self, **kwds):
            for attr in self.__slots__:
                setattr(self, attr, kwds.get(attr))

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

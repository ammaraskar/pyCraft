from minecraft.networking.packets import Packet
from minecraft.networking.types import (
    VarInt, Float, RelativeHand, ClickType, multi_attribute_alias, Vector
)


class UseEntityPacket(Packet):
    @staticmethod
    def get_id(context):
        return 0x0E if context.protocol_version >= 464 else \
               0x0D if context.protocol_version >= 389 else \
               0x0B if context.protocol_version >= 386 else \
               0x0A if context.protocol_version >= 345 else \
               0x09 if context.protocol_version >= 343 else \
               0x0A if context.protocol_version >= 336 else \
               0x0B if context.protocol_version >= 318 else \
               0x0A if context.protocol_version >= 94 else \
               0x09 if context.protocol_version >= 70 else \
               0x02

    packet_name = "use entity"

    fields = ('entity_id', 'click_type', 'target_x', 'target_y', 'target_z',
              'hand')

    def read(self, file_object):
        self.entity_id = VarInt.read(file_object)
        self.click_type = VarInt.read(file_object)

        if self.click_type is ClickType.INTERACT_AT:
            for attr in 'target_x', 'target_y', 'target_z':
                setattr(self, attr, Float.read(file_object))

        if self.click_type in [ClickType.INTERACT_AT, ClickType.INTERACT]:
            self.hand = VarInt.read(file_object)

    def write_fields(self, packet_buffer):
        # pylint: disable=no-member
        VarInt.send(self.entity_id, packet_buffer)
        VarInt.send(self.click_type, packet_buffer)

        if self.click_type is ClickType.INTERACT_AT:
            for attr in self.target_x, self.target_y, self.target_z:
                Float.send(attr, packet_buffer)

        if self.click_type in [ClickType.INTERACT_AT, ClickType.INTERACT]:
            VarInt.send(self.hand, packet_buffer)

    ClickType = ClickType

    Hand = RelativeHand

    # Access the 'target_{x,y,z}' fields as a Vector.
    target = multi_attribute_alias(Vector, 'target_x', 'target_y', 'target_z')

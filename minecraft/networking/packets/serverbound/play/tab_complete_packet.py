from minecraft.networking.types import VarInt, Boolean, Position, String
from minecraft.networking.packets import Packet


class TabCompletePacket(Packet):
    @staticmethod
    def get_id(context):
        return 0x06 if context.protocol_later_eq(464) else \
               0x05 if context.protocol_later_eq(389) else \
               0x04 if context.protocol_later_eq(345) else \
               0x01 if context.protocol_later_eq(336) else \
               0x02 if context.protocol_later_eq(318) else \
               0x01 if context.protocol_later_eq(94) else \
               0x00 if context.protocol_later_eq(70) else \
               0x15 if context.protocol_later_eq(69) else \
               0x14
    packet_name = 'tab complete'

    @property
    def fields(self):
        fields = 'text',
        if self.context.protocol_later_eq(351):
            fields += 'transaction_id'
        else:
            fields += 'has_position', 'looked_at_block',
            if self.context.protocol_later_eq(95):
                fields += 'assume_command'

    def read(self, file_object):
        self.transaction_id = VarInt.read(file_object) \
            if self.context.protocol_later_eq(351) else None
        self.text = String.read(file_object)
        if self.context.protocol_earlier_eq(350):
            self.assume_command = Boolean.read(file_object) \
                if self.context.protocol_later_eq(95) else None
            has_position = Boolean.read(file_object)
            if has_position:
                self.looked_at_block = Position.read(file_object)

    def write_fields(self, packet_buffer):
        if self.context.protocol_later_eq(351):
            VarInt.send(self.transaction_id, packet_buffer)
        String.send(self.text, packet_buffer)
        if self.context.protocol_earlier_eq(350):
            if self.context.protocol_later_eq(95):
                Boolean.send(self.assume_command, packet_buffer)
            Boolean.send(self.looked_at_block is not None, packet_buffer)
            if self.looked_at_block is not None:
                Position.send(self.looked_at_block, packet_buffer)

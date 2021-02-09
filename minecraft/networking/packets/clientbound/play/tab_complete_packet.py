from minecraft.networking.packets import Packet
from minecraft.networking.types import VarInt, Boolean, String, MutableRecord

class TabCompletePacket(Packet):
    @staticmethod
    def get_id(context):
        return 0x0F if context.protocol_later_eq(741) else \
               0x10 if context.protocol_later_eq(721) else \
               0x11 if context.protocol_later_eq(550) else \
               0x10 if context.protocol_later_eq(345) else \
               0x0E if context.protocol_later_eq(332) else \
               0x0F if context.protocol_later_eq(318) else \
               0x0E if context.protocol_later_eq(70) else \
               0x3A

    packet_name = 'tab complete'
    @property
    def fields():
        fields = 'matches',
        if self.context.protocol_later_eq(346):
            fields += 'transaction_id', 'start', 'length',
        return fields

    class TabMatch(MutableRecord):
        __slots__ = ('match', 'tooltip')
        
        def __init__(self, match, tooltip=None):
            self.match = match
            self.tooltip = tooltip
    
    def read(self, file_object):
        if self.context.protocol_later_eq(346):
            self.transaction_id = VarInt.read(file_object)
            self.start = VarInt.read(file_object)
            self.length = VarInt.read(file_object)
        count = VarInt.read(file_object)
        self.matches = []
        for i in range(count):
            match = String.read(file_object)
            has_tooltip = False
            if self.context.protocol_later_eq(357):
                has_tooltip = Boolean.read(file_object)
            tooltip = String.read(file_object) if has_tooltip else None
            tabmatch = TabCompletePacket.TabMatch(match, tooltip)
            self.matches.append(tabmatch)
    def write_fields(self, packet_buffer):
        if self.context.protocol_later_eq(346):
            VarInt.send(self.transaction_id, packet_buffer)
            VarInt.send(self.start, packet_buffer)
            VarInt.send(self.length, packet_buffer)
        VarInt.send(len(self.matches), packet_buffer)
        for tabmatch in self.matches:
            String.send(tabmatch.match, packet_buffer)
            if self.context.protocol_later_eq(357):
                Boolean.send(tabmatch.tooltip is not None, packet_buffer)
                if tabmatch.tooltip is not None:
                    String.send(tabmatch.tooltip, packet_buffer)

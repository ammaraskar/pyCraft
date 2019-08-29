from minecraft.networking.packets import Packet

from minecraft.networking.types import VarInt



class DestroyEntitiesPacket(Packet):
    @staticmethod
    def get_id(context):
        return 0x37 if context.protocol_version >= 471 else \
               0x35 if context.protocol_version >= 461 else \
               0x36 if context.protocol_version >= 451 else \
               0x35 if context.protocol_version >= 389 else \
               0x34 if context.protocol_version >= 352 else \
               0x33 if context.protocol_version >= 345 else \
               0x32 if context.protocol_version >= 336 else \
               0x31 if context.protocol_version >= 332 else \
               0x32 if context.protocol_version >= 318 else \
               0x30 if context.protocol_version >= 70 else \
               0x13

    def read(self, file_object):
        self.entity_ids = [VarInt.read(file_object)
                           for i in range(VarInt.read(file_object))]

    def write(self, packet_buffer):
        count = len(self.entity_ids)
        VarInt.send(count, packet_buffer)
        for entity_id in self.entity_ids:
            VarInt.send(entity_id, packet_buffer)
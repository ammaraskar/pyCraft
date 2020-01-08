from minecraft.networking.packets import Packet
from minecraft.networking.types import (
    VarInt, Integer, UnsignedByte, Position, Vector, MutableRecord,
    attribute_alias, multi_attribute_alias,
)


class BlockChangePacket(Packet):
    @staticmethod
    def get_id(context):
        return 0x0C if context.protocol_version >= 550 else \
               0x0B if context.protocol_version >= 332 else \
               0x0C if context.protocol_version >= 318 else \
               0x0B if context.protocol_version >= 67 else \
               0x24 if context.protocol_version >= 62 else \
               0x23

    packet_name = 'block change'
    definition = [
        {'location': Position},
        {'block_state_id': VarInt}]
    block_state_id = 0

    # For protocols < 347: an accessor for (block_state_id >> 4).
    @property
    def blockId(self):
        return self.block_state_id >> 4

    @blockId.setter
    def blockId(self, block_id):
        self.block_state_id = (self.block_state_id & 0xF) | (block_id << 4)

    # For protocols < 347: an accessor for (block_state_id & 0xF).
    @property
    def blockMeta(self):
        return self.block_state_id & 0xF

    @blockMeta.setter
    def blockMeta(self, meta):
        self.block_state_id = (self.block_state_id & ~0xF) | (meta & 0xF)

    # This alias is retained for backward compatibility.
    blockStateId = attribute_alias('block_state_id')


class MultiBlockChangePacket(Packet):
    @staticmethod
    def get_id(context):
        return 0x10 if context.protocol_version >= 550 else \
               0x0F if context.protocol_version >= 343 else \
               0x10 if context.protocol_version >= 332 else \
               0x11 if context.protocol_version >= 318 else \
               0x10 if context.protocol_version >= 67 else \
               0x22

    packet_name = 'multi block change'

    fields = 'chunk_x', 'chunk_z', 'records'

    # Access the 'chunk_x' and 'chunk_z' fields as a tuple.
    chunk_pos = multi_attribute_alias(tuple, 'chunk_x', 'chunk_z')

    class Record(MutableRecord):
        __slots__ = 'x', 'y', 'z', 'block_state_id'

        def __init__(self, **kwds):
            self.block_state_id = 0
            super(MultiBlockChangePacket.Record, self).__init__(**kwds)

        # Access the 'x', 'y', 'z' fields as a Vector of ints.
        position = multi_attribute_alias(Vector, 'x', 'y', 'z')

        # For protocols < 347: an accessor for (block_state_id >> 4).
        @property
        def blockId(self):
            return self.block_state_id >> 4

        @blockId.setter
        def blockId(self, block_id):
            self.block_state_id = self.block_state_id & 0xF | block_id << 4

        # For protocols < 347: an accessor for (block_state_id & 0xF).
        @property
        def blockMeta(self):
            return self.block_state_id & 0xF

        @blockMeta.setter
        def blockMeta(self, meta):
            self.block_state_id = self.block_state_id & ~0xF | meta & 0xF

        # This alias is retained for backward compatibility.
        blockStateId = attribute_alias('block_state_id')

        def read(self, file_object):
            h_position = UnsignedByte.read(file_object)
            self.x, self.z = h_position >> 4, h_position & 0xF
            self.y = UnsignedByte.read(file_object)
            self.block_state_id = VarInt.read(file_object)

        def write(self, packet_buffer):
            UnsignedByte.send(self.x << 4 | self.z & 0xF, packet_buffer)
            UnsignedByte.send(self.y, packet_buffer)
            VarInt.send(self.block_state_id, packet_buffer)

    def read(self, file_object):
        self.chunk_x = Integer.read(file_object)
        self.chunk_z = Integer.read(file_object)
        records_count = VarInt.read(file_object)
        self.records = []
        for i in range(records_count):
            record = self.Record()
            record.read(file_object)
            self.records.append(record)

    def write_fields(self, packet_buffer):
        Integer.send(self.chunk_x, packet_buffer)
        Integer.send(self.chunk_z, packet_buffer)
        VarInt.send(len(self.records), packet_buffer)
        for record in self.records:
            record.write(packet_buffer)

from minecraft.networking.packets import Packet
from minecraft.networking.types import (
    Type, VarInt, VarLong, UnsignedLong, Integer, UnsignedByte, Position,
    Vector, MutableRecord, PrefixedArray, Boolean, attribute_alias,
    multi_attribute_alias,
)


class BlockChangePacket(Packet):
    @staticmethod
    def get_id(context):
        return 0x0B if context.protocol_later_eq(721) else \
               0x0C if context.protocol_later_eq(550) else \
               0x0B if context.protocol_later_eq(332) else \
               0x0C if context.protocol_later_eq(318) else \
               0x0B if context.protocol_later_eq(67) else \
               0x24 if context.protocol_later_eq(62) else \
               0x23

    packet_name = 'block change'
    definition = [
        {'location': Position},
        {'block_state_id': VarInt}]
    block_state_id = 0

    # For protocols before 347: an accessor for (block_state_id >> 4).
    @property
    def blockId(self):
        return self.block_state_id >> 4

    @blockId.setter
    def blockId(self, block_id):
        self.block_state_id = (self.block_state_id & 0xF) | (block_id << 4)

    # For protocols before 347: an accessor for (block_state_id & 0xF).
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
        return 0x3B if context.protocol_later_eq(741) else \
               0x0F if context.protocol_later_eq(721) else \
               0x10 if context.protocol_later_eq(550) else \
               0x0F if context.protocol_later_eq(343) else \
               0x10 if context.protocol_later_eq(332) else \
               0x11 if context.protocol_later_eq(318) else \
               0x10 if context.protocol_later_eq(67) else \
               0x22

    packet_name = 'multi block change'

    # Only used in protocol 741 and later.
    class ChunkSectionPos(Vector, Type):
        @classmethod
        def read(cls, file_object):
            value = UnsignedLong.read(file_object)
            y = value | ~0xFFFFF if value & 0x80000 else value & 0xFFFFF
            value >>= 20
            z = value | ~0x3FFFFF if value & 0x200000 else value & 0x3FFFFF
            value >>= 22
            x = value | ~0x3FFFFF if value & 0x200000 else value
            return cls(x, y, z)

        @classmethod
        def send(cls, pos, socket):
            x, y, z = pos
            value = (x & 0x3FFFFF) << 42 | (z & 0x3FFFFF) << 20 | y & 0xFFFFF
            UnsignedLong.send(value, socket)

    class Record(MutableRecord, Type):
        __slots__ = 'x', 'y', 'z', 'block_state_id'

        def __init__(self, **kwds):
            self.block_state_id = 0
            super(MultiBlockChangePacket.Record, self).__init__(**kwds)

        # Access the 'x', 'y', 'z' fields as a Vector of ints.
        position = multi_attribute_alias(Vector, 'x', 'y', 'z')

        # For protocols before 347: an accessor for (block_state_id >> 4).
        @property
        def blockId(self):
            return self.block_state_id >> 4

        @blockId.setter
        def blockId(self, block_id):
            self.block_state_id = self.block_state_id & 0xF | block_id << 4

        # For protocols before 347: an accessor for (block_state_id & 0xF).
        @property
        def blockMeta(self):
            return self.block_state_id & 0xF

        @blockMeta.setter
        def blockMeta(self, meta):
            self.block_state_id = self.block_state_id & ~0xF | meta & 0xF

        # This alias is retained for backward compatibility.
        blockStateId = attribute_alias('block_state_id')

        @classmethod
        def read_with_context(cls, file_object, context):
            record = cls()
            if context.protocol_later_eq(741):
                value = VarLong.read(file_object)
                record.block_state_id = value >> 12
                record.x = (value >> 8) & 0xF
                record.z = (value >> 4) & 0xF
                record.y = value & 0xF
            else:
                h_position = UnsignedByte.read(file_object)
                record.x = h_position >> 4
                record.z = h_position & 0xF
                record.y = UnsignedByte.read(file_object)
                record.block_state_id = VarInt.read(file_object)
            return record

        @classmethod
        def send_with_context(self, record, socket, context):
            if context.protocol_later_eq(741):
                value = record.block_state_id << 12 | \
                        (record.x & 0xF) << 8 | \
                        (record.z & 0xF) << 4 | \
                        record.y & 0xF
                VarLong.send(value, socket)
            else:
                UnsignedByte.send(record.x << 4 | record.z & 0xF, socket)
                UnsignedByte.send(record.y, socket)
                VarInt.send(record.block_state_id, socket)

    get_definition = staticmethod(lambda context: [
        {'chunk_section_pos': MultiBlockChangePacket.ChunkSectionPos},
        {'invert_trust_edges': Boolean}
        if context.protocol_later_eq(748) else {},  # Provisional field name.
        {'records': PrefixedArray(VarInt, MultiBlockChangePacket.Record)},
    ] if context.protocol_later_eq(741) else [
        {'chunk_x': Integer},
        {'chunk_z': Integer},
        {'records': PrefixedArray(VarInt, MultiBlockChangePacket.Record)},
    ])

    # Access the 'chunk_x' and 'chunk_z' fields as a tuple.
    # Only used prior to protocol 741.
    chunk_pos = multi_attribute_alias(tuple, 'chunk_x', 'chunk_z')

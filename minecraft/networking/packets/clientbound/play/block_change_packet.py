from minecraft.networking.packets import Packet
from minecraft.networking.types import (
    VarInt, Integer, UnsignedByte, Position, Vector
)


class BlockChangePacket(Packet):
    @staticmethod
    def get_id(context):
        return 0x0B if context.protocol_version >= 332 else \
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
    def blockId(self, block_id):
        self.block_state_id = (self.block_state_id & 0xF) | (block_id << 4)
    blockId = property(lambda self: self.block_state_id >> 4, blockId)

    # For protocols < 347: an accessor for (block_state_id & 0xF).
    def blockMeta(self, meta):
        self.block_state_id = (self.block_state_id & ~0xF) | (meta & 0xF)
    blockMeta = property(lambda self: self.block_state_id & 0xF, blockMeta)

    # This alias is retained for backward compatibility.
    def blockStateId(self, block_state_id):
        self.block_state_id = block_state_id
    blockStateId = property(lambda self: self.block_state_id, blockStateId)


class MultiBlockChangePacket(Packet):
    @staticmethod
    def get_id(context):
        return 0x0F if context.protocol_version >= 343 else \
               0x10 if context.protocol_version >= 332 else \
               0x11 if context.protocol_version >= 318 else \
               0x10 if context.protocol_version >= 67 else \
               0x22

    packet_name = 'multi block change'

    class Record(object):
        __slots__ = 'x', 'y', 'z', 'block_state_id'

        def __init__(self, **kwds):
            self.block_state_id = 0
            for attr, value in kwds.items():
                setattr(self, attr, value)

        def __repr__(self):
            return '%s(%s)' % (type(self).__name__, ', '.join(
                   '%s=%r' % (a, getattr(self, a)) for a in self.__slots__))

        def __eq__(self, other):
            return type(self) is type(other) and all(
                getattr(self, a) == getattr(other, a) for a in self.__slots__)

        # Access the 'x', 'y', 'z' fields as a Vector of ints.
        def position(self, position):
            self.x, self.y, self.z = position
        position = property(lambda r: Vector(r.x, r.y, r.z), position)

        # For protocols < 347: an accessor for (block_state_id >> 4).
        def blockId(self, block_id):
            self.block_state_id = self.block_state_id & 0xF | block_id << 4
        blockId = property(lambda r: r.block_state_id >> 4, blockId)

        # For protocols < 347: an accessor for (block_state_id & 0xF).
        def blockMeta(self, meta):
            self.block_state_id = self.block_state_id & ~0xF | meta & 0xF
        blockMeta = property(lambda r: r.block_state_id & 0xF, blockMeta)

        # This alias is retained for backward compatibility.
        def blockStateId(self, block_state_id):
            self.block_state_id = block_state_id
        blockStateId = property(lambda r: r.block_state_id, blockStateId)

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

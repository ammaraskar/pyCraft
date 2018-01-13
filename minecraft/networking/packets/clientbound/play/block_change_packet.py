from minecraft.networking.packets import (
    Packet, PacketBuffer
)
from minecraft.networking.types import (
    VarInt, Integer, UnsignedByte, Position
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

    def read(self, file_object):
        self.location = Position.read(file_object)
        blockData = VarInt.read(file_object)
        if self.context.protocol_version >= 347:
            # See comments on MultiBlockChangePacket.OpaqueRecord.
            self.blockStateId = blockData
        else:
            self.blockId = (blockData >> 4)
            self.blockMeta = (blockData & 0xF)

    def write(self, socket, compression_threshold=None):
        packet_buffer = PacketBuffer()
        (x, y, z) = self.location
        Position.send(x, y, z, packet_buffer)
        blockData = ((self.blockId << 4) | (self.blockMeta & 0xF))
        VarInt.send(blockData)
        self._write_buffer(socket, packet_buffer, compression_threshold)


class MultiBlockChangePacket(Packet):
    @staticmethod
    def get_id(context):
        return 0x0F if context.protocol_version >= 343 else \
               0x10 if context.protocol_version >= 332 else \
               0x11 if context.protocol_version >= 318 else \
               0x10 if context.protocol_version >= 67 else \
               0x22

    packet_name = 'multi block change'

    class BaseRecord(object):
        __slots__ = 'x', 'y', 'z'

        def __init__(self, horizontal_position, y_coordinate):
            self.x = (horizontal_position & 0xF0) >> 4
            self.y = y_coordinate
            self.z = (horizontal_position & 0x0F)

        def __str__(self):
            return self.__repr__()

        @classmethod
        def get_subclass(cls, context):
            return MultiBlockChangePacket.OpaqueRecord \
                   if context.protocol_version >= 347 else \
                   MultiBlockChangePacket.Record

    class Record(BaseRecord):
        __slots__ = 'blockId', 'blockMeta'

        def __init__(self, h_position, y_coordinate, blockData):
            super(MultiBlockChangePacket.Record, self).__init__(
                h_position, y_coordinate)
            self.blockId = (blockData >> 4)
            self.blockMeta = (blockData & 0xF)

        def __repr__(self):
            return ('Record(x=%s, y=%s, z=%s, blockId=%s)'
                    % (self.x, self.y, self.z, self.blockId))

    '''The structure of the block data changed in protocol 347 (17w47b,
       between 1.12.2 and 1.13), which this class reflects: instead of a
       separate blockId and blockMeta number, there is a single opaque
       blockStateId whose meaning may change between minor versions.'''
    class OpaqueRecord(BaseRecord):
        __slots__ = 'blockStateId'

        def __init__(self, h_position, y_coordinate, blockData):
            super(MultiBlockChangePacket.OpaqueRecord, self).__init__(
                h_position, y_coordinate)
            self.blockStateId = blockData

        def __repr__(self):
            return ('OpaqueRecord(x=%s, y=%s, z=%s, blockStateId=%s)'
                    % (self.x, self.y, self.z, self.blockStateId))

    def read(self, file_object):
        self.chunk_x = Integer.read(file_object)
        self.chunk_z = Integer.read(file_object)
        records_count = VarInt.read(file_object)
        record_type = self.BaseRecord.get_subclass(self.context)
        self.records = []
        for i in range(records_count):
            record = record_type(h_position=UnsignedByte.read(file_object),
                                 y_coordinate=VarInt.read(file_object),
                                 blockData=VarInt.read(file_object))
            self.records.append(record)

    def write(self, socket, compression_threshold=None):
        raise NotImplementedError

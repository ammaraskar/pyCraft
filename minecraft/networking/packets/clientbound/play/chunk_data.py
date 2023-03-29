from math import floor

from minecraft.networking.packets import Packet, PacketBuffer
from minecraft.networking.types import (
    VarInt, Integer, Boolean, Nbt, UnsignedByte, Long, Short,
    multi_attribute_alias, Vector, UnsignedLong
)


class ChunkDataPacket(Packet):
    @staticmethod
    def get_id(context):
        return 0x22  # FIXME

    packet_name = 'chunk data'
    fields = 'x', 'bit_mask_y', 'z', 'full_chunk'

    def read(self, file_object):
        self.x = Integer.read(file_object)
        self.z = Integer.read(file_object)
        self.full_chunk = Boolean.read(file_object)
        self.bit_mask_y = VarInt.read(file_object)
        self.heightmaps = Nbt.read(file_object)
        self.biomes = []
        if self.full_chunk:
            for i in range(1024):
                self.biomes.append(Integer.read(file_object))
        size = VarInt.read(file_object)
        self.data = file_object.read(size)
        size_entities = VarInt.read(file_object)
        self.entities = []
        for i in range(size_entities):
            self.entities.append(Nbt.read(file_object))

        self.decode_chunk_data()

    def write_fields(self, packet_buffer):
        Integer.send(self.x, packet_buffer)
        Integer.send(self.z, packet_buffer)
        Boolean.send(self.full_chunk, packet_buffer)
        VarInt.send(self.bit_mask_y, packet_buffer)
        Nbt.send(self.heightmaps, packet_buffer)
        if self.full_chunk:
            for i in range(1024):
                Integer.send(self.biomes[i], packet_buffer)
        VarInt.send(len(self.data), packet_buffer)
        packet_buffer.send(self.data)
        VarInt.send(len(self.entities), packet_buffer)
        for e in self.entities:
            Nbt.send(e, packet_buffer)

    def decode_chunk_data(self):
        packet_data = PacketBuffer()
        packet_data.send(self.data)
        packet_data.reset_cursor()

        self.chunks = {}
        for i in range(16):  # 0-15
            self.chunks[i] = Chunk(self.x, i, self.z)
            if self.bit_mask_y & (1 << i):
                self.chunks[i].read(packet_data)

        for e in self.entities:
            y = e['y']
            self.chunks[floor(y/16)].entities.append(e)


class Chunk:

    position = multi_attribute_alias(Vector, 'x', 'y', 'z')

    def __init__(self, x, y, z, empty=True):
        self.x = x
        self.y = y
        self.z = z
        self.empty = empty
        self.entities = []

    def __repr__(self):
        return 'Chunk(%r, %r, %r)' % (self.x, self.y, self.z)

    def read(self, file_object):
        self.empty = False
        self.block_count = Short.read(file_object)
        self.bpb = UnsignedByte.read(file_object)
        if self.bpb <= 4:
            self.bpb = 4

        if self.bpb <= 8:  # Indirect palette
            self.palette = []
            size = VarInt.read(file_object)
            for i in range(size):
                self.palette.append(VarInt.read(file_object))
        else:  # Direct palette
            self.palette = None

        size = VarInt.read(file_object)
        longs = []
        for i in range(size):
            longs.append(UnsignedLong.read(file_object))

        self.blocks = []
        mask = (1 << self.bpb)-1
        for i in range(4096):
            l1 = int((i*self.bpb)/64)
            offset = (i*self.bpb) % 64
            l2 = int(((i+1)*self.bpb-1)/64)
            n = longs[l1] >> offset
            if l2 > l1:
                n |= longs[l2] << (64-offset)
            n &= mask
            if self.palette:
                n = self.palette[n]
            self.blocks.append(n)

    def write_fields(self, packet_buffer):
        pass  # TODO

    def get_block_at(self, x, y, z):
        if self.empty:
            return 0
        return self.blocks[x+y*256+z*16]

    def set_block_at(self, x, y, z, block):
        if self.empty:
            self.init_empty()
        self.blocks[x+y*256+z*16] = block

    def init_empty(self):
        self.blocks = []
        for i in range(4096):
            self.blocks.append(0)
        self.empty = False

    @property
    def origin(self):
        return self.position*16

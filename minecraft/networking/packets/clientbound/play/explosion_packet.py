from minecraft.networking.types import (
    Vector, Float, Byte, Integer, multi_attribute_alias,
)
from minecraft.networking.packets import Packet


class ExplosionPacket(Packet):
    @staticmethod
    def get_id(context):
        return 0x1D if context.protocol_version >= 550 else \
               0x1C if context.protocol_version >= 471 else \
               0x1E if context.protocol_version >= 389 else \
               0x1D if context.protocol_version >= 345 else \
               0x1C if context.protocol_version >= 332 else \
               0x1D if context.protocol_version >= 318 else \
               0x1C if context.protocol_version >= 80 else \
               0x1B if context.protocol_version >= 67 else \
               0x27

    packet_name = 'explosion'

    fields = 'x', 'y', 'z', 'radius', 'records', \
             'player_motion_x', 'player_motion_y', 'player_motion_z'

    # Access the 'x', 'y', 'z' fields as a Vector tuple.
    position = multi_attribute_alias(Vector, 'x', 'y', 'z')

    # Access the 'player_motion_{x,y,z}' fields as a Vector tuple.
    player_motion = multi_attribute_alias(
        Vector, 'player_motion_x', 'player_motion_y', 'player_motion_z')

    class Record(Vector):
        __slots__ = ()

    def read(self, file_object):
        self.x = Float.read(file_object)
        self.y = Float.read(file_object)
        self.z = Float.read(file_object)
        self.radius = Float.read(file_object)
        records_count = Integer.read(file_object)
        self.records = []
        for i in range(records_count):
            rec_x = Byte.read(file_object)
            rec_y = Byte.read(file_object)
            rec_z = Byte.read(file_object)
            record = ExplosionPacket.Record(rec_x, rec_y, rec_z)
            self.records.append(record)
        self.player_motion_x = Float.read(file_object)
        self.player_motion_y = Float.read(file_object)
        self.player_motion_z = Float.read(file_object)

    def write_fields(self, packet_buffer):
        Float.send(self.x, packet_buffer)
        Float.send(self.y, packet_buffer)
        Float.send(self.z, packet_buffer)
        Float.send(self.radius, packet_buffer)
        Integer.send(len(self.records), packet_buffer)
        for record in self.records:
            Byte.send(record.x, packet_buffer)
            Byte.send(record.y, packet_buffer)
            Byte.send(record.z, packet_buffer)
        Float.send(self.player_motion_x, packet_buffer)
        Float.send(self.player_motion_y, packet_buffer)
        Float.send(self.player_motion_z, packet_buffer)

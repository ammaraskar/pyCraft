from minecraft.networking.types import (
    VarInt, Double, Boolean, OriginPoint, Vector, multi_attribute_alias
)

from minecraft.networking.packets import Packet


class FacePlayerPacket(Packet):
    @staticmethod
    def get_id(context):
        return 0x35 if context.protocol_version >= 550 else \
               0x34 if context.protocol_version >= 471 else \
               0x32 if context.protocol_version >= 451 else \
               0x31 if context.protocol_version >= 389 else \
               0x30

    packet_name = 'face player'

    @property
    def fields(self):
        return ('origin', 'x', 'y', 'z', 'entity_id', 'entity_origin') \
               if self.context.protocol_version >= 353 else \
               ('entity_id', 'x', 'y', 'z')

    # Access the 'x', 'y', 'z' fields as a Vector tuple.
    target = multi_attribute_alias(Vector, 'x', 'y', 'z')

    def read(self, file_object):
        if self.context.protocol_version >= 353:
            self.origin = VarInt.read(file_object)
            self.x = Double.read(file_object)
            self.y = Double.read(file_object)
            self.z = Double.read(file_object)
            is_entity = Boolean.read(file_object)
            if is_entity:
                # If the entity given by entity ID cannot be found,
                # this packet should be treated as if is_entity was false.
                self.entity_id = VarInt.read(file_object)
                self.entity_origin = VarInt.read(file_object)
            else:
                self.entity_id = None

        else:  # Protocol version 352
            is_entity = Boolean.read(file_object)
            self.entity_id = VarInt.read(file_object) if is_entity else None
            if not is_entity:
                self.x = Double.read(file_object)
                self.y = Double.read(file_object)
                self.z = Double.read(file_object)

    def write_fields(self, packet_buffer):
        if self.context.protocol_version >= 353:
            VarInt.send(self.origin, packet_buffer)
            Double.send(self.x, packet_buffer)
            Double.send(self.y, packet_buffer)
            Double.send(self.z, packet_buffer)
            if self.entity_id is not None:
                Boolean.send(True, packet_buffer)
                VarInt.send(self.entity_id, packet_buffer)
                VarInt.send(self.entity_origin, packet_buffer)
            else:
                Boolean.send(False, packet_buffer)

        else:  # Protocol version 352
            if self.entity_id is not None:
                Boolean.send(True, packet_buffer)
                VarInt.send(self.entity_id, packet_buffer)
            else:
                Boolean.send(False, packet_buffer)
                Double.send(self.x, packet_buffer)
                Double.send(self.y, packet_buffer)
                Double.send(self.z, packet_buffer)

    # These aliases declare the Enum type corresponding to each field:
    Origin = OriginPoint
    EntityOrigin = OriginPoint

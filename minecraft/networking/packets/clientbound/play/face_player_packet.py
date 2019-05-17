from minecraft.networking.types import (
    VarInt, Double, Boolean, FeetEyes
)

from minecraft.networking.packets import Packet


class FacePlayerPacket(Packet):
    @staticmethod
    def get_id(context):
        return 0x34 if context.protocol_version >= 471 else \
               0x32 if context.protocol_version >= 451 else \
               0x31 if context.protocol_version >= 389 else \
               0x30

    packet_name = 'face player'

    def read(self, file_object):
        if self.context.protocol_version >= 353:
            self.feet_or_eyes = VarInt.read(file_object)
            self.x = Double.read(file_object)
            self.y = Double.read(file_object)
            self.z = Double.read(file_object)
            is_entity = Boolean.read(file_object)
            if is_entity:
                # If the entity given by entity ID cannot be found,
                # this packet should be treated as if is_entity was false.
                self.entity_id = VarInt.read(file_object)
                self.entity_feet_or_eyes = VarInt.read(file_object)

        else:  # Protocol version 352
            is_entity = Boolean.read(file_object)
            self.entity_id = VarInt.read(file_object) if is_entity else None
            if not is_entity:
                self.x = Double.read(file_object)
                self.y = Double.read(file_object)
                self.z = Double.read(file_object)

    def write_fields(self, packet_buffer):
        if self.context.protocol_version >= 353:
            VarInt.send(self.feet_or_eyes, packet_buffer)
            Double.send(self.x, packet_buffer)
            Double.send(self.y, packet_buffer)
            Double.send(self.z, packet_buffer)
            if self.entity_id:
                VarInt.send(self.entity_id, packet_buffer)
                VarInt.send(self.entity_feet_or_eyes, packet_buffer)

        else:  # Protocol version 352
            if self.entity_id:
                Boolean.send(True, packet_buffer)
                VarInt.send(self.entity_id, packet_buffer)
            else:
                Boolean.send(False, packet_buffer)
                Double.send(self.x, packet_buffer)
                Double.send(self.y, packet_buffer)
                Double.send(self.z, packet_buffer)

    # FacePlayerPacket.FeetEyes is an alias for FeetEyes
    FeetEyes = FeetEyes
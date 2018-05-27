from minecraft.networking.packets import Packet

from minecraft.networking.types import (
    VarInt, UUID, Byte, Double, Integer, UnsignedByte, Short, Enum, Vector,
    PositionAndLook
)


class SpawnObjectPacket(Packet):
    @staticmethod
    def get_id(context):
        return 0x00 if context.protocol_version >= 67 else \
               0x0E

    packet_name = 'spawn object'

    class EntityType(Enum):
        BOAT = 1
        ITEM_STACK = 2
        AREA_EFFECT_CLOUD = 3
        MINECART = 10
        ACTIVATED_TNT = 50
        ENDERCRYSTAL = 51
        ARROW = 60
        SNOWBALL = 61
        EGG = 62
        FIREBALL = 63
        FIRECHARGE = 64
        ENDERPERL = 65
        WITHER_SKULL = 66
        SHULKER_BULLET = 67
        LLAMA_SPIT = 68
        FALLING_OBJECT = 70
        ITEM_FRAMES = 71
        EYE_OF_ENDER = 72
        POTION = 73
        EXP_BOTTLE = 75
        FIREWORK_ROCKET = 76
        LEASH_KNOT = 77
        ARMORSTAND = 78
        EVOCATION_FANGS = 79
        FISHING_HOOK = 90
        SPECTRAL_ARROW = 91
        DRAGON_FIREBALL = 93

    def read(self, file_object):
        self.entity_id = VarInt.read(file_object)
        if self.context.protocol_version >= 49:
            self.object_uuid = UUID.read(file_object)
        self.type_id = Byte.read(file_object)

        xyz_type = Double if self.context.protocol_version >= 100 else Integer
        for attr in 'x', 'y', 'z':
            setattr(self, attr, xyz_type.read(file_object))
        for attr in 'pitch', 'yaw':
            setattr(self, attr, UnsignedByte.read(file_object))

        self.data = Integer.read(file_object)
        if self.context.protocol_version >= 49 or self.data > 0:
            for attr in 'velocity_x', 'velocity_y', 'velocity_z':
                setattr(self, attr, Short.read(file_object))

    def write_fields(self, packet_buffer):
        VarInt.send(self.entity_id, packet_buffer)
        if self.context.protocol_version >= 49:
            UUID.send(self.object_uuid, packet_buffer)
        Byte.send(self.type_id, packet_buffer)

        xyz_type = Double if self.context.protocol_version >= 100 else Integer
        for coord in self.x, self.y, self.z:
            xyz_type.send(coord, packet_buffer)
        for coord in self.pitch, self.yaw:
            UnsignedByte.send(coord, packet_buffer)

        Integer.send(self.data, packet_buffer)
        if self.context.protocol_version >= 49 or self.data > 0:
            for coord in self.velocity_x, self.velocity_y, self.velocity_z:
                Short.send(coord, packet_buffer)

    # Access the entity type as a string, according to the EntityType enum.
    def type(self, type_name):
        self.type_id = getattr(self.EntityType, type_name)
    type = property(lambda p: p.EntityType.name_from_value(p.type_id), type)

    # Access the fields 'x', 'y', 'z' as a Vector.
    def position(self, position):
        self.x, self.y, self.z = position
    position = property(lambda p: Vector(p.x, p.y, p.z), position)

    # Access the fields 'x', 'y', 'z', 'yaw', 'pitch' as a PositionAndLook.
    # NOTE: modifying the object retrieved from this property will not change
    # the packet; it can only be changed by attribute or property assignment.
    def position_and_look(self, position_and_look):
        self.x, self.y, self.z = position_and_look.position
        self.yaw, self.pitch = position_and_look.look
    position_and_look = property(lambda p: PositionAndLook(
                            x=p.x, y=p.y, z=p.z, yaw=p.yaw, pitch=p.pitch),
                            position_and_look)

    # Access the fields 'velocity_x', 'velocity_y', 'velocity_z' as a Vector.
    def velocity(self, velocity):
        self.velocity_x, self.velocity_y, self.velocity_z = velocity
    velocity = property(lambda p: Vector(p.velocity_x, p.velocity_y,
                                         p.velocity_z), velocity)

    # This alias is retained for backward compatibility.
    def objectUUID(self, object_uuid):
        self.object_uuid = object_uuid
    objectUUID = property(lambda self: self.object_uuid, objectUUID)

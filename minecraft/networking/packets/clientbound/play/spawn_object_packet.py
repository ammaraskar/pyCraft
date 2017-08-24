from minecraft.networking.packets import Packet

from minecraft.networking.types import (
    VarInt, UUID, Byte, Double, Integer, UnsignedByte, Short, Enum
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
        if self._context.protocol_version >= 49:
            self.objectUUID = UUID.read(file_object)
        type_id = Byte.read(file_object)
        self.type = SpawnObjectPacket.EntityType.name_from_value(type_id)

        if self._context.protocol_version >= 100:
            self.x = Double.read(file_object)
            self.y = Double.read(file_object)
            self.z = Double.read(file_object)
        else:
            self.x = Integer.read(file_object)
            self.y = Integer.read(file_object)
            self.z = Integer.read(file_object)

        self.pitch = UnsignedByte.read(file_object)
        self.yaw = UnsignedByte.read(file_object)
        self.data = Integer.read(file_object)

        if self._context.protocol_version < 49:
            if self.data > 0:
                self.velocity_x = Short.read(file_object)
                self.velocity_y = Short.read(file_object)
                self.velocity_z = Short.read(file_object)
        else:
            self.velocity_x = Short.read(file_object)
            self.velocity_y = Short.read(file_object)
            self.velocity_z = Short.read(file_object)

    def write(self, socket, compression_threshold=None):
        raise NotImplementedError

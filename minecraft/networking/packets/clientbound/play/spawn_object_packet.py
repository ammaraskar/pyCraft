from minecraft.networking.packets import Packet
from minecraft.networking.types.utility import descriptor

from minecraft.networking.types import (
    VarInt, UUID, Byte, Double, Integer, Angle, Short, Enum, Vector,
    Direction, PositionAndLook, attribute_alias, multi_attribute_alias,
)


class SpawnObjectPacket(Packet):
    @staticmethod
    def get_id(context):
        return 0x00 if context.protocol_version >= 67 else \
               0x0E

    packet_name = 'spawn object'

    fields = ('entity_id', 'object_uuid', 'type_id', 'x', 'y', 'z', 'pitch',
              'yaw', 'data', 'velocity_x', 'velocity_y', 'velocity_z')

    @descriptor
    def EntityType(desc, self, cls):  # pylint: disable=no-self-argument
        if self is None:
            # EntityType is being accessed as a class attribute.
            raise AttributeError(
                'This interface is deprecated:\n\n'
                'As of pyCraft\'s support for Minecraft 1.14, the nested '
                'class "SpawnObjectPacket.EntityType" cannot be accessed as a '
                'class attribute, because it depends on the protocol version. '
                'There are two ways to access the correct version of the '
                'class:\n\n'
                '1. Access the "EntityType" attribute of a '
                '"SpawnObjectPacket" instance with its "context" property '
                'set.\n\n'
                '2. Call "SpawnObjectPacket.field_enum(\'type_id\', '
                'context)".')
        else:
            # EntityType is being accessed as an instance attribute.
            return self.field_enum('type_id', self.context)

    @classmethod
    def field_enum(cls, field, context):
        if field != 'type_id' or context is None:
            return

        pv = context.protocol_version
        name = 'EntityType_%d' % pv
        if hasattr(cls, name):
            return getattr(cls, name)

        class EntityType(Enum):
            ACTIVATED_TNT     = 50 if pv < 458 else 55  # PrimedTnt
            AREA_EFFECT_CLOUD =  3 if pv < 458 else  0
            ARMORSTAND        = 78 if pv < 458 else  1
            ARROW             = 60 if pv < 458 else  2
            BOAT              =  1 if pv < 458 else  5
            DRAGON_FIREBALL   = 93 if pv < 458 else 13
            EGG               = 62 if pv < 458 else 74  # ThrownEgg
            ENDERCRYSTAL      = 51 if pv < 458 else 16
            ENDERPEARL        = 65 if pv < 458 else 75  # ThrownEnderpearl
            EVOCATION_FANGS   = 79 if pv < 458 else 20
            EXP_BOTTLE        = 75 if pv < 458 else 76  # ThrownExpBottle
            EYE_OF_ENDER      = 72 if pv < 458 else 23  # EyeOfEnderSignal
            FALLING_OBJECT    = 70 if pv < 458 else 24  # FallingSand
            FIREBALL          = 63 if pv < 458 else 34  # Fireball (ghast)
            FIRECHARGE        = 64 if pv < 458 else 65  # SmallFireball (blaze)
            FIREWORK_ROCKET   = 76 if pv < 458 else 25  # FireworksRocketEntity
            FISHING_HOOK      = 90 if pv < 458 else 93  # Fishing bobber
            ITEM_FRAMES       = 71 if pv < 458 else 33  # ItemFrame
            ITEM_STACK        =  2 if pv < 458 else 32  # Item
            LEASH_KNOT        = 77 if pv < 458 else 35
            LLAMA_SPIT        = 68 if pv < 458 else 37
            MINECART          = 10 if pv < 458 else 39  # MinecartRideable
            POTION            = 73 if pv < 458 else 77  # ThrownPotion
            SHULKER_BULLET    = 67 if pv < 458 else 60
            SNOWBALL          = 61 if pv < 458 else 67
            SPECTRAL_ARROW    = 91 if pv < 458 else 68
            WITHER_SKULL      = 66 if pv < 458 else 85
            if pv >= 393:
                TRIDENT = 94
            if pv >= 458:
                MINECART_CHEST =         40
                MINECART_COMMAND_BLOCK = 41
                MINECART_FURNACE =       42
                MINECART_HOPPER =        43
                MINECART_SPAWNER =       44
                MINECART_TNT =           45

        setattr(cls, name, EntityType)
        return EntityType

    def read(self, file_object):
        self.entity_id = VarInt.read(file_object)
        if self.context.protocol_version >= 49:
            self.object_uuid = UUID.read(file_object)

        if self.context.protocol_version >= 458:
            self.type_id = VarInt.read(file_object)
        else:
            self.type_id = Byte.read(file_object)

        xyz_type = Double if self.context.protocol_version >= 100 else Integer
        for attr in 'x', 'y', 'z':
            setattr(self, attr, xyz_type.read(file_object))
        for attr in 'pitch', 'yaw':
            setattr(self, attr, Angle.read(file_object))

        self.data = Integer.read(file_object)
        if self.context.protocol_version >= 49 or self.data > 0:
            for attr in 'velocity_x', 'velocity_y', 'velocity_z':
                setattr(self, attr, Short.read(file_object))

    def write_fields(self, packet_buffer):
        VarInt.send(self.entity_id, packet_buffer)
        if self.context.protocol_version >= 49:
            UUID.send(self.object_uuid, packet_buffer)

        if self.context.protocol_version >= 458:
            VarInt.send(self.type_id, packet_buffer)
        else:
            Byte.send(self.type_id, packet_buffer)

        # pylint: disable=no-member
        xyz_type = Double if self.context.protocol_version >= 100 else Integer
        for coord in self.x, self.y, self.z:
            xyz_type.send(coord, packet_buffer)
        for coord in self.pitch, self.yaw:
            Angle.send(coord, packet_buffer)

        Integer.send(self.data, packet_buffer)
        if self.context.protocol_version >= 49 or self.data > 0:
            for coord in self.velocity_x, self.velocity_y, self.velocity_z:
                Short.send(coord, packet_buffer)

    # Access the entity type as a string, according to the EntityType enum.
    @property
    def type(self):
        if self.context is None:
            raise ValueError('This packet must have a non-None "context" '
                             'in order to read the "type" property.')
        # pylint: disable=no-member
        return self.EntityType.name_from_value(self.type_id)

    @type.setter
    def type(self, type_name):
        if self.context is None:
            raise ValueError('This packet must have a non-None "context" '
                             'in order to set the "type" property.')
        self.type_id = getattr(self.EntityType, type_name)

    @type.deleter
    def type(self):
        del self.type_id

    # Access the 'x', 'y', 'z' fields as a Vector.
    position = multi_attribute_alias(Vector, 'x', 'y', 'z')

    # Access the 'yaw', 'pitch' fields as a Direction.
    look = multi_attribute_alias(Direction, 'yaw', 'pitch')

    # Access the 'x', 'y', 'z', 'pitch', 'yaw' fields as a PositionAndLook.
    # NOTE: modifying the object retrieved from this property will not change
    # the packet; it can only be changed by attribute or property assignment.
    position_and_look = multi_attribute_alias(
        PositionAndLook, x='x', y='y', z='z', yaw='yaw', pitch='pitch')

    # Access the 'velocity_{x,y,z}' fields as a Vector.
    velocity = multi_attribute_alias(
        Vector, 'velocity_x', 'velocity_y', 'velocity_z')

    # This alias is retained for backward compatibility.
    objectUUID = attribute_alias('object_uuid')

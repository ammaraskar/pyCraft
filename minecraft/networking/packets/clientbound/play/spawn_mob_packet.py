from minecraft.networking.packets import Packet
from minecraft.networking.types.utility import descriptor

from minecraft.networking.types import (
    VarInt, UUID, Double, Integer, Angle, Short, UnsignedByte,
    Enum, Vector, Direction, PositionAndLook, attribute_alias,
    multi_attribute_alias
)


class SpawnMobPacket(Packet):
    @staticmethod
    def get_id(context):
        return 0x03 if context.protocol_version >= 70 else \
               0x0F

    packet_name = 'spawn mob'

    fields = ('entity_id', 'entity_uuid', 'type_id', 'x', 'y', 'z', 'pitch',
              'yaw', 'head_pitch', 'velocity_x', 'velocity_y', 'velocity_z')

    @classmethod
    def field_enum(cls, field, context):
        if field != 'type_id' or context is None:
            return

        pv = context.protocol_version
        name = "EntityType_%d" % pv
        if hasattr(cls, name):
            return getattr(cls, name)

        class EntityType(Enum):
            BAT                 = 3  if pv >= 393 else \
                                  65
            BLAZE               = 4  if pv >= 393 else \
                                  61
            CAVE_SPIDER         = 7  if pv >= 447 else \
                                  6  if pv >= 393 else \
                                  59
            CHICKEN             = 8  if pv >= 447 else \
                                  7  if pv >= 393 else \
                                  93
            COW                 = 10 if pv >= 447 else \
                                  9  if pv >= 393 else \
                                  92
            CREEPER             = 11 if pv >= 447 else \
                                  10 if pv >= 393 else \
                                  50
            ENDER_DRAGON        = 18 if pv >= 447 else \
                                  17 if pv >= 393 else \
                                  63
            ENDERMAN            = 19 if pv >= 447 else \
                                  18 if pv >= 393 else \
                                  58
            ENDERMITE           = 20 if pv >= 447 else \
                                  19 if pv >= 393 else \
                                  67
            GHAST               = 28 if pv >= 447 else \
                                  26 if pv >= 393 else \
                                  56
            GIANT               = 29 if pv >= 447 else \
                                  27 if pv >= 393 else \
                                  53
            GUARDIAN            = 30 if pv >= 447 else \
                                  28 if pv >= 393 else \
                                  68
            MAGMA_CUBE          = 40 if pv >= 447 else \
                                  38 if pv >= 393 else \
                                  62 # Lava Slime
            MOOSHROOM           = 49 if pv >= 447 else \
                                  47 if pv >= 393 else \
                                  96 # Mushroom Cow
            OCELOT              = 50 if pv >= 447 else \
                                  48 if pv >= 393 else \
                                  98 # Ozelot
            PIG                 = 54 if pv >= 447 else \
                                  51 if pv >= 393 else \
                                  90
            ZOMBIE_PIGMAN       = 56 if pv >= 447 else \
                                  53 if pv >= 393 else \
                                  57
            RABBIT              = 59 if pv >= 447 else \
                                  56 if pv >= 393 else \
                                  101
            SHEEP               = 61 if pv >= 447 else \
                                  58 if pv >= 393 else \
                                  91
            SILVERFISH          = 64 if pv >= 447 else \
                                  61 if pv >= 393 else \
                                  60
            SKELETON            = 65 if pv >= 447 else \
                                  62 if pv >= 393 else \
                                  51
            SLIME               = 67 if pv >= 447 else \
                                  64 if pv >= 393 else \
                                  55
            SNOW_GOLEM          = 69 if pv >= 447 else \
                                  66 if pv >= 393 else \
                                  97 # Snow Man
            SPIDER              = 72 if pv >= 447 else \
                                  69 if pv >= 393 else \
                                  52
            SQUID               = 73 if pv >= 447 else \
                                  70 if pv >= 393 else \
                                  94
            VILLAGER            = 84 if pv >= 447 else \
                                  79 if pv >= 393 else \
                                  120
            IRON_GOLEM          = 85 if pv >= 447 else \
                                  80 if pv >= 393 else \
                                  99 # Villager Golem
            WITCH               = 89 if pv >= 447 else \
                                  82 if pv >= 393 else \
                                  66
            WITHER              = 90 if pv >= 447 else \
                                  83 if pv >= 393 else \
                                  64 # Wither Boss
            # Issue with Wither Skeletons in PrismarineJS?
            # Not present in some protocol versions so
            # only 99% certain this enum is 100% accurate.
            WITHER_SKELETON     = 91 if pv >= 447 else \
                                  84 if pv >= 393 else \
                                  5
            WOLF                = 93 if pv >= 447 else \
                                  86 if pv >= 393 else \
                                  95
            ZOMBIE              = 94 if pv >= 447 else \
                                  87 if pv >= 393 else \
                                  54
            if pv >= 447:
                TRADER_LLAMA        = 75
            if pv >= 393:
                COD                 = 9  if pv >= 447 else \
                                      8
                DOLPHIN             = 13 if pv >= 447 else \
                                      12
                DROWNED             = 15 if pv >= 447 else \
                                      14
                PUFFERFISH          = 55 if pv >= 447 else \
                                      52
                SALMON              = 60 if pv >= 447 else \
                                      57
                TROPICAL_FISH       = 76 if pv >= 447 else \
                                      72
                TURTLE              = 77 if pv >= 447 else \
                                      73
                PHANTOM             = 97 if pv >= 447 else \
                                      90
            if pv >= 335:
                ILLUSIONER          = 33 if pv >= 447 else \
                                      31 if pv >= 393 else \
                                      37 # Illusion Illager
                PARROT              = 53 if pv >= 447 else \
                                      50 if pv >= 393 else \
                                      105
            if pv >= 315:
                DONKEY              = 12 if pv >= 447 else \
                                      11 if pv >= 393 else \
                                      31
                ELDER_GUARDIAN      = 16 if pv >= 447 else \
                                      15 if pv >= 393 else \
                                      4
                EVOKER              = 22 if pv >= 447 else \
                                      21 if pv >= 393 else \
                                      34
                HORSE               = 31 if pv >= 447 else \
                                      29 if pv >= 393 else \
                                      100
                HUSK                = 32 if pv >= 447 else \
                                      30 if pv >= 393 else \
                                      23
                LLAMA               = 38 if pv >= 447 else \
                                      36 if pv >= 393 else \
                                      103
                MULE                = 48 if pv >= 447 else \
                                      46 if pv >= 393 else \
                                      32
                POLAR_BEAR          = 57 if pv >= 447 else \
                                      54 if pv >= 393 else \
                                      102
                SKELETON_HORSE      = 66 if pv >= 447 else \
                                      63 if pv >= 393 else \
                                      28
                STRAY               = 74 if pv >= 447 else \
                                      71 if pv >= 393 else \
                                      6
                VEX                 = 83 if pv >= 447 else \
                                      78 if pv >= 393 else \
                                      35
                VINDICATOR          = 86 if pv >= 447 else \
                                      81 if pv >= 393 else \
                                      36  # Vindication Illager
                ZOMBIE_HORSE        = 95 if pv >= 447 else \
                                      88 if pv >= 393 else \
                                      29
                ZOMBIE_VILLAGER     = 96 if pv >= 447 else \
                                      89 if pv >= 393 else \
                                      27
            if pv >= 76:
                SHULKER             = 62 if pv >= 447 else \
                                      59 if pv >= 393 else \
                                      69

        setattr(cls, name, EntityType)
        return EntityType

    def read(self, file_object):
        self.entity_id = VarInt.read(file_object)
        if self.context.protocol_version >= 69:
            self.entity_uuid = UUID.read(file_object)

        if self.context.protocol_version >= 301:
            self.type_id = VarInt.read(file_object)
        else:
            self.type_id = UnsignedByte.read(file_object)

        xyz_type = Double if self.context.protocol_version >= 97 else Integer
        for attr in 'x', 'y', 'z':
            setattr(self, attr, xyz_type.read(file_object))

        for attr in 'pitch', 'yaw', 'head_pitch':
            setattr(self, attr, Angle.read(file_object))

        for attr in 'velocity_x', 'velocity_y', 'velocity_z':
            setattr(self, attr, Short.read(file_object))

        # TODO: read entity metadata

    def write_fields(self, packet_buffer):
        VarInt.read(self.entity_id, packet_buffer)
        if self.context.protocol_version >= 69:
            UUID.send(self.entity_id, packet_buffer)

        if self.context.protocol_version >= 301:
            VarInt.send(self.type_id, packet_buffer)
        else:
            UnsignedByte.send(self.type_id, packet_buffer)

        xyz_type = Double if self.context.protocol_version >= 97 else Integer
        for coord in self.x, self.y, self.z:
            xyz_type.send(coord, packet_buffer)

        for angle in self.pitch, self.yaw, self.head_pitch:
            Angle.send(angle, packet_buffer)

        for velocity in self.velocity_x, self.velocity_y, self.velocity_z:
            Short.send(velocity, packet_buffer)

        # TODO: write entity metadata

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


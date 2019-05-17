"""Types for enumerations of values occurring in packets, including operations
   for working with these values.

   The values in an enum are given as class attributes with UPPERCASE names.

   These classes are usually not supposed to be instantiated, but sometimes an
   instantiatable class may subclass Enum to provide class enum attributes in
   addition to other functionality.
"""
from .utility import Vector


__all__ = (
    'Enum', 'BitFieldEnum', 'AbsoluteHand', 'RelativeHand', 'BlockFace',
    'Difficulty', 'Dimension', 'GameMode', 'OriginPoint'
)


class Enum(object):
    # Return a human-readable string representation of an enum value.
    @classmethod
    def name_from_value(cls, value):
        for name, name_value in cls.__dict__.items():
            if name.isupper() and name_value == value:
                return name


class BitFieldEnum(Enum):
    @classmethod
    def name_from_value(cls, value):
        if not isinstance(value, int):
            return
        ret_names = []
        ret_value = 0
        for cls_name, cls_value in sorted(
            [(n, v) for (n, v) in cls.__dict__.items()
             if isinstance(v, int) and n.isupper() and v | value == value],
            reverse=True, key=lambda p: p[1]
        ):
            if ret_value | cls_value != ret_value or cls_value == value:
                ret_names.append(cls_name)
                ret_value |= cls_value
        if ret_value == value:
            return '|'.join(reversed(ret_names)) if ret_names else '0'


# Designation of one of a player's hands, in absolute terms.
class AbsoluteHand(Enum):
    LEFT = 0
    RIGHT = 1


# Designation of one a player's hands, relative to a choice of main/off hand.
class RelativeHand(Enum):
    MAIN = 0
    OFF = 1


# Designation of one of a block's 6 faces.
class BlockFace(Enum):
    BOTTOM = 0  # -Y
    TOP = 1     # +Y
    NORTH = 2   # -Z
    SOUTH = 3   # +Z
    WEST = 4    # -X
    EAST = 5    # +X

    # A dict mapping Vector tuples to the corresponding BlockFace values.
    # When accessing this dict, plain tuples also match. For example:
    #   >>> BlockFace.from_vector[0, 0, -1] == BlockFace.NORTH
    #   True
    from_vector = {
        Vector(0, -1, 0): BOTTOM,
        Vector(0, +1, 0): TOP,
        Vector(0, 0, -1): NORTH,
        Vector(0, 0, +1): SOUTH,
        Vector(-1, 0, 0): WEST,
        Vector(+1, 0, 0): EAST,
    }

    # A dict mapping BlockFace values to unit Position tuples.
    # This is the inverse mapping of face_by_position. For example:
    #   >>> BlockFace.to_vector[BlockFace.NORTH]
    #   Position(x=0, y=0, z=-1)
    to_vector = {fce: pos for (pos, fce) in from_vector.items()}


# Designation of a world's difficulty.
class Difficulty(Enum):
    PEACEFUL = 0
    EASY = 1
    NORMAL = 2
    HARD = 3


# Designation of a world's dimension.
class Dimension(Enum):
    NETHER = -1
    OVERWORLD = 0
    END = 1


# Designation of a player's gamemode.
class GameMode(Enum):
    SURVIVAL = 0
    CREATIVE = 1
    ADVENTURE = 2
    SPECTATOR = 3


# Currently designates an entity's feet or eyes.
# Used in the Face Player Packet
class OriginPoint(Enum):
    FEET = 0
    EYES = 1

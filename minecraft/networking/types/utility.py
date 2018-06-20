"""Minecraft data types that are used by packets, but don't have a specific
   network representation.
"""
from collections import namedtuple


__all__ = (
    'Vector', 'MutableRecord', 'PositionAndLook',
)


"""An immutable type usually used to represent 3D spatial coordinates.
   NOTE: subclasses of 'Vector' should have '__slots__ = ()' to avoid the
   creation of a '__dict__' attribute, which would waste space.
"""
Vector = namedtuple('Vector', ('x', 'y', 'z'))


class MutableRecord(object):
    """An abstract base class providing namedtuple-like repr(), ==, and hash()
       implementations for types containing mutable fields given by __slots__.
    """
    __slots__ = ()

    def __init__(self, **kwds):
        for attr, value in kwds.items():
            setattr(self, attr, value)

    def __repr__(self):
        return '%s(%s)' % (type(self).__name__, ', '.join(
               '%s=%r' % (a, getattr(self, a)) for a in self.__slots__))

    def __eq__(self, other):
        return type(self) is type(other) and \
            all(getattr(self, a) == getattr(other, a) for a in self.__slots__)

    def __hash__(self):
        return hash(getattr(self, a) for a in self.__slots__)


class PositionAndLook(MutableRecord):
    """A mutable record containing 3 spatial position coordinates
       and 2 rotational coordinates for a look direction.
    """
    __slots__ = 'x', 'y', 'z', 'yaw', 'pitch'

    # Access the fields 'x', 'y', 'z' as a Vector.
    def position(self, position):
        self.x, self.y, self.z = position
    position = property(lambda self: Vector(self.x, self.y, self.z), position)

    # Access the fields 'yaw', 'pitch' as a tuple.
    def look(self, look):
        self.yaw, self.pitch = look
    look = property(lambda self: (self.yaw, self.pitch), look)

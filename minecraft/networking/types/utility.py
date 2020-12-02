"""Minecraft data types that are used by packets, but don't have a specific
   network representation.
"""
from collections import namedtuple

# These aliases are retained for backward compatibility
from minecraft.utility import (  # noqa: F401
    descriptor, overridable_descriptor, overridable_property, attribute_alias,
    multi_attribute_alias, attribute_transform, class_and_instancemethod,
)


class Vector(namedtuple('BaseVector', ('x', 'y', 'z'))):
    """An immutable type usually used to represent 3D spatial coordinates,
       supporting elementwise vector addition, subtraction, and negation; and
       scalar multiplication and (right) division.

       NOTE: subclasses of 'Vector' should have '__slots__ = ()' to avoid the
       creation of a '__dict__' attribute, which would waste space.
    """
    __slots__ = ()

    def __add__(self, other):
        return NotImplemented if not isinstance(other, Vector) else \
               type(self)(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return NotImplemented if not isinstance(other, Vector) else \
               type(self)(self.x - other.x, self.y - other.y, self.z - other.z)

    def __neg__(self):
        return type(self)(-self.x, -self.y, -self.z)

    def __mul__(self, other):
        return type(self)(self.x*other, self.y*other, self.z*other)

    def __rmul__(self, other):
        return type(self)(other*self.x, other*self.y, other*self.z)

    def __truediv__(self, other):
        return type(self)(self.x/other, self.y/other, self.z/other)

    def __floordiv__(self, other):
        return type(self)(self.x//other, self.y//other, self.z//other)

    __div__ = __floordiv__

    def __repr__(self):
        return '%s(%r, %r, %r)' % (type(self).__name__, self.x, self.y, self.z)


class MutableRecord(object):
    """An abstract base class providing namedtuple-like repr(), ==, hash(), and
       iter(), implementations for types containing mutable fields given by
       __slots__.
    """
    __slots__ = ()

    def __init__(self, **kwds):
        for attr, value in kwds.items():
            setattr(self, attr, value)

    def __repr__(self):
        return '%s(%s)' % (type(self).__name__, ', '.join(
            '%s=%r' % (a, getattr(self, a)) for a in self._all_slots()
            if hasattr(self, a)))

    def __eq__(self, other):
        return type(self) is type(other) and all(
            getattr(self, a) == getattr(other, a) for a in self._all_slots())

    def __ne__(self, other):
        return not (self == other)

    def __hash__(self):
        values = tuple(getattr(self, a, None) for a in self._all_slots())
        return hash((type(self), values))

    def __iter__(self):
        return iter(getattr(self, a) for a in self._all_slots())

    @classmethod
    def _all_slots(cls):
        for supcls in reversed(cls.__mro__):
            slots = supcls.__dict__.get('__slots__', ())
            slots = (slots,) if isinstance(slots, str) else slots
            for slot in slots:
                yield slot


Direction = namedtuple('Direction', ('yaw', 'pitch'))


class PositionAndLook(MutableRecord):
    """A mutable record containing 3 spatial position coordinates
       and 2 rotational coordinates for a look direction.
    """
    __slots__ = 'x', 'y', 'z', 'yaw', 'pitch'

    position = multi_attribute_alias(Vector, 'x', 'y', 'z')

    look = multi_attribute_alias(Direction, 'yaw', 'pitch')

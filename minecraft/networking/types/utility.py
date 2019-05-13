"""Minecraft data types that are used by packets, but don't have a specific
   network representation.
"""
from __future__ import division
from collections import namedtuple


__all__ = (
    'Vector', 'MutableRecord', 'descriptor',
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

    def __ne__(self, other):
        return not (self == other)

    def __hash__(self):
        values = tuple(getattr(self, a, None) for a in self.__slots__)
        return hash((type(self), values))


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


class descriptor(object):
    """Behaves identically to the builtin 'property' function of Python,
       except that the getter, setter and deleter functions given by the
       user are used as the raw __get__, __set__ and __delete__ functions
       as defined in Python's descriptor protocol.
    """
    __slots__ = '_fget', '_fset', '_fdel'

    def __init__(self, fget=None, fset=None, fdel=None):
        self._fget = fget if fget is not None else self._default_get
        self._fset = fset if fset is not None else self._default_set
        self._fdel = fdel if fdel is not None else self._default_del

    def getter(self, fget):
        self._fget = fget
        return self

    def setter(self, fset):
        self._fset = fset
        return self

    def deleter(self, fdel):
        self._fdel = fdel
        return self

    @staticmethod
    def _default_get(instance, owner):
        raise AttributeError('unreadable attribute')

    @staticmethod
    def _default_set(instance, value):
        raise AttributeError("can't set attribute")

    @staticmethod
    def _default_del(instance):
        raise AttributeError("can't delete attribute")

    def __get__(self, instance, owner):
        return self._fget(self, instance, owner)

    def __set__(self, instance, value):
        return self._fset(self, instance, value)

    def __delete__(self, instance):
        return self._fdel(self, instance)

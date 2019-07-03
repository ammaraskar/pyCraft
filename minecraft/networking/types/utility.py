"""Minecraft data types that are used by packets, but don't have a specific
   network representation.
"""
from __future__ import division

from collections import namedtuple
from itertools import chain


__all__ = (
    'Vector', 'MutableRecord', 'Direction', 'PositionAndLook', 'descriptor',
    'attribute_alias', 'multi_attribute_alias',
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


def attribute_alias(name):
    """An attribute descriptor that redirects access to a different attribute
       with a given name.
    """
    return property(fget=(lambda self: getattr(self, name)),
                    fset=(lambda self, value: setattr(self, name, value)),
                    fdel=(lambda self: delattr(self, name)))


def multi_attribute_alias(container, *arg_names, **kwd_names):
    """A descriptor for an attribute whose value is a container of a given type
       with several fields, each of which is aliased to a different attribute
       of the parent object.

       The 'n'th name in 'arg_names' is the parent attribute that will be
       aliased to the field of 'container' settable by the 'n'th positional
       argument to its constructor, and accessible as its 'n'th iterable
       element.

       As a special case, 'tuple' may be given as the 'container' when there
       are positional arguments, and (even though the tuple constructor does
       not take positional arguments), the arguments will be aliased to the
       corresponding positions in a tuple.

       The name in 'kwd_names' mapped to by the key 'k' is the parent attribute
       that will be aliased to the field of 'container' settable by the keyword
       argument 'k' to its constructor, and accessible as its 'k' attribute.
    """
    if container is tuple:
        container = lambda *args: args  # noqa: E731

    @property
    def alias(self):
        return container(
            *(getattr(self, name) for name in arg_names),
            **{kwd: getattr(self, name) for (kwd, name) in kwd_names.items()})

    @alias.setter
    def alias(self, values):
        if arg_names:
            for name, value in zip(arg_names, values):
                setattr(self, name, value)
        for kwd, name in kwd_names.items():
            setattr(self, name, getattr(values, kwd))

    @alias.deleter
    def alias(self):
        for name in chain(arg_names, kwd_names.values()):
            delattr(self, name)

    return alias


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


Direction = namedtuple('Direction', ('yaw', 'pitch'))


class PositionAndLook(MutableRecord):
    """A mutable record containing 3 spatial position coordinates
       and 2 rotational coordinates for a look direction.
    """
    __slots__ = 'x', 'y', 'z', 'yaw', 'pitch'

    position = multi_attribute_alias(Vector, 'x', 'y', 'z')

    look = multi_attribute_alias(Direction, 'yaw', 'pitch')

"""Minecraft data types that are used by packets, but don't have a specific
   network representation.
"""
from collections import namedtuple
from itertools import chain
import types

# These aliases are retained for backward compatibility
from minecraft.utility import (  # noqa: F401
    descriptor, overridable_descriptor, overridable_property, attribute_alias,
    multi_attribute_alias, attribute_transform, class_and_instancemethod,
)


__all__ = (
    'Vector', 'MutableRecord', 'Direction', 'PositionAndLook',
    'LookAndDirection', 'PositionLookAndDirection', 'descriptor',
    'overridable_descriptor', 'overridable_property',
    'attribute_alias', 'attribute_transform', 'multi_attribute_alias',
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
        return type(self)(self.x * other, self.y * other, self.z * other)

    def __rmul__(self, other):
        return type(self)(other * self.x, other * self.y, other * self.z)

    def __truediv__(self, other):
        return type(self)(self.x / other, self.y / other, self.z / other)

    def __floordiv__(self, other):
        return type(self)(self.x // other, self.y // other, self.z // other)

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
        return isinstance(self, type(other)) and all(
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


def attribute_transform(name, from_orig, to_orig):
    """An attribute descriptor that provides a view of a different attribute
       with a given name via a given transformation and its given inverse."""
    return property(
        fget=(lambda self: from_orig(getattr(self, name))),
        fset=(lambda self, value: setattr(self, name, to_orig(value))),
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

class overridable_descriptor:
    """As 'descriptor' (defined below), except that only a getter can be
       defined, and the resulting descriptor has no '__set__' or '__delete__'
       methods defined; hence, attributes defined via this class can be
       overridden by attributes of instances of the class in which it occurs.
    """
    __slots__ = '_fget',

    def __init__(self, fget=None):
        self._fget = fget if fget is not None else self._default_get

    def getter(self, fget):
        self._fget = fget
        return self

    @staticmethod
    def _default_get(instance, owner):
        raise AttributeError('unreadable attribute')

    def __get__(self, instance, owner):
        return self._fget(self, instance, owner)


class overridable_property(overridable_descriptor):
    """As the builtin 'property' decorator of Python, except that only
       a getter is defined and the resulting descriptor is a non-data
       descriptor, overridable by attributes of instances of the class
       in which the property occurs. See also 'overridable_descriptor' above.
    """
    def __get__(self, instance, _owner):
        return self._fget(instance)


# class descriptor(object):
#     """Behaves identically to the builtin 'property' function of Python,
#        except that the getter, setter and deleter functions given by the
#        user are used as the raw __get__, __set__ and __delete__ functions
#        as defined in Python's descriptor protocol.
#     """
#     __slots__ = '_fget', '_fset', '_fdel'

#     def __init__(self, fget=None, fset=None, fdel=None):
#         self._fget = fget if fget is not None else self._default_get
#         self._fset = fset if fset is not None else self._default_set
#         self._fdel = fdel if fdel is not None else self._default_del

#     def getter(self, fget):
#         self._fget = fget
#         return self

#     def setter(self, fset):
#         self._fset = fset
#         return self

#     def deleter(self, fdel):
#         self._fdel = fdel
#         return self

#     @staticmethod
#     def _default_get(instance, owner):
#         raise AttributeError('unreadable attribute')

#     @staticmethod
#     def _default_set(instance, value):
#         raise AttributeError("can't set attribute")

#     @staticmethod
#     def _default_del(instance):
#         raise AttributeError("can't delete attribute")

#     def __get__(self, instance, owner):
#         return self._fget(self, instance, owner)

#     def __set__(self, instance, value):
#         return self._fset(self, instance, value)

#     def __delete__(self, instance):
#         return self._fdel(self, instance)

# class class_and_instancemethod:
#     """ A decorator for functions defined in a class namespace which are to be
#         accessed as both class and instance methods: retrieving the method from
#         a class will return a bound class method (like the built-in
#         'classmethod' decorator), but retrieving the method from an instance
#         will return a bound instance method (as if the function were not
#         decorated). Therefore, the first argument of the decorated function may
#         be either a class or an instance, depending on how it was called.
#     """

#     __slots__ = '_func',

#     def __init__(self, func):
#         self._func = func

#     def __get__(self, inst, owner=None):
#         bind_to = owner if inst is None else inst
#         return types.MethodType(self._func, bind_to)

Direction = namedtuple('Direction', ('yaw', 'pitch'))


class PositionAndLook(MutableRecord):
    """A mutable record containing 3 spatial position coordinates
       and 2 rotational coordinates for a look direction.
    """
    __slots__ = 'x', 'y', 'z', 'yaw', 'pitch'

    position = multi_attribute_alias(Vector, 'x', 'y', 'z')

    look = multi_attribute_alias(Direction, 'yaw', 'pitch')


LookAndDirection = namedtuple('LookAndDirection',
                              ('yaw', 'pitch', 'head_pitch'))


class PositionLookAndDirection(MutableRecord):
    """
    A mutable record containing 3 spatial position coordinates,
    2 rotational components and an additional rotational component for
    the head of the object.
    """
    __slots__ = 'x', 'y', 'z', 'yaw', 'pitch', 'head_pitch'

    position = multi_attribute_alias(Vector, 'x', 'y', 'z')

    look = multi_attribute_alias(Direction, 'yaw', 'pitch')

    look_and_direction = multi_attribute_alias(LookAndDirection,
                                               'yaw', 'pitch', 'head_pitch')
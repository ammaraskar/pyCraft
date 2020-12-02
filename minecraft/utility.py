""" Miscellaneous general utilities.
"""
import types
from itertools import chain

from . import PROTOCOL_VERSION_INDICES


def protocol_earlier(pv1, pv2):
    """ Returns True if protocol version 'pv1' was published before 'pv2',
        or else returns False.
    """
    return PROTOCOL_VERSION_INDICES[pv1] < PROTOCOL_VERSION_INDICES[pv2]


def protocol_earlier_eq(pv1, pv2):
    """ Returns True if protocol versions 'pv1' and 'pv2' are the same or if
        'pv1' was published before 'pv2', or else returns False.
    """
    return PROTOCOL_VERSION_INDICES[pv1] <= PROTOCOL_VERSION_INDICES[pv2]


def attribute_transform(name, from_orig, to_orig):
    """An attribute descriptor that provides a view of a different attribute
       with a given name via a given transformation and its given inverse."""
    return property(
        fget=(lambda self: from_orig(getattr(self, name))),
        fset=(lambda self, value: setattr(self, name, to_orig(value))),
        fdel=(lambda self: delattr(self, name)))


def attribute_alias(name):
    """An attribute descriptor that redirects access to a different attribute
       with a given name.
    """
    return attribute_transform(name, lambda x: x, lambda x: x)


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


class descriptor(overridable_descriptor):
    """Behaves identically to the builtin 'property' decorator of Python,
       except that the getter, setter and deleter functions given by the
       user are used as the raw __get__, __set__ and __delete__ functions
       as defined in Python's descriptor protocol.

       Since an instance of this class always havs '__set__' and '__delete__'
       defined, it is a "data descriptor", so its binding behaviour cannot be
       overridden in instances of the class in which it occurs. See
       https://docs.python.org/3/reference/datamodel.html#descriptor-invocation
       for more information. See also 'overridable_descriptor' above.
    """
    __slots__ = '_fset', '_fdel'

    def __init__(self, fget=None, fset=None, fdel=None):
        super(descriptor, self).__init__(fget=fget)
        self._fset = fset if fset is not None else self._default_set
        self._fdel = fdel if fdel is not None else self._default_del

    def setter(self, fset):
        self._fset = fset
        return self

    def deleter(self, fdel):
        self._fdel = fdel
        return self

    @staticmethod
    def _default_set(instance, value):
        raise AttributeError("can't set attribute")

    @staticmethod
    def _default_del(instance):
        raise AttributeError("can't delete attribute")

    def __set__(self, instance, value):
        return self._fset(self, instance, value)

    def __delete__(self, instance):
        return self._fdel(self, instance)


class class_and_instancemethod:
    """ A decorator for functions defined in a class namespace which are to be
        accessed as both class and instance methods: retrieving the method from
        a class will return a bound class method (like the built-in
        'classmethod' decorator), but retrieving the method from an instance
        will return a bound instance method (as if the function were not
        decorated). Therefore, the first argument of the decorated function may
        be either a class or an instance, depending on how it was called.
    """

    __slots__ = '_func',

    def __init__(self, func):
        self._func = func

    def __get__(self, inst, owner=None):
        bind_to = owner if inst is None else inst
        return types.MethodType(self._func, bind_to)

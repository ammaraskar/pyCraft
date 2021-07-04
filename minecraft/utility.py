""" Miscellaneous general utilities.
"""
import types
import re
import json
from itertools import chain

from . import PROTOCOL_VERSION_INDICES

colors = {'random': '&u','obfuscated':'&k', 'bold':'&l', 'strikethrough':'&m', 'underlined':'&n', 'italic':'&o', 'reset':'&r',  'black':'&0', 'dark_blue':'&1', 'dark_green':'&2', 'dark_aqua':'&3', 'dark_red':'&4', 'dark_purple':'&5', 'gold':'&6', 'gray':'&7', 'dark_gray':'&8', 'blue':'&9', 'green':'&a', 'aqua':'&b', 'red':'&c', 'light_purple':'&d', 'yellow':'&e', 'white':'&f'}
pycolors = {"&r": "\x1b[0m", "&f": "\x1b[0m", "&l": "\x1b[1m", "&o": "\x1b[3m", "&n": "\x1b[4m", "&m": "\x1b[9m", "&0": "\x1b[30m", "&4": "\x1b[31m", "&2": "\x1b[32m", "&6": "\x1b[33m", "&1": "\x1b[34m", "&5": "\x1b[35m", "&3": "\x1b[36m", "&7": "\x1b[37m", "&8": "\x1b[90m", "&c": "\x1b[91m", "&a": "\x1b[92m", "&e": "\x1b[93m", "&9": "\x1b[94m", "&d": "\x1b[95m", "&b": "\x1b[96m"}

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

class chat_component:
    def __init__(self, chatMessage):
        if type(chatMessage) == str: chatMessage = json.loads(chatMessage)
        self.chatMessage = chatMessage
    
    def toPlaintText(self):
        chatMessage = (self.__parse(self.chatMessage) if "text" in self.chatMessage else "") + "".join([self.__parse(extra) for extra in (self.chatMessage["extra"] if "extra" in self.chatMessage else []) + (self.chatMessage["with"] if "with" in self.chatMessage else [])])
        if chatMessage.startswith("&f"): chatMessage = chatMessage.replace("&f", "", 1)
        return chatMessage
    
    def __parse(self, obj):
        obj = {"text": obj} if type(obj) == str else obj
        return "{color}{tags}{text}".format(tags=" ".join([colors[b] for b in obj if (type(obj[b]) is bool and obj[b])]), color=colors[obj.get("color", "white")], text=obj.get("text", ""))
    
    def toColored(self):
        return re.sub(u"([&%][0-9a-zA-Z])", self.__escape, self.toPlaintText().replace(chr(167), '&')) + "\x1b[0m"
    
    def __escape(self, TextC):
        return pycolors[TextC.group(1).lower()] if TextC.group(1).lower() in pycolors else TextC.group()

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

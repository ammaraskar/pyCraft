#!/usr/bin/env python
# -*- coding: utf8 -*-
"""
Implements reading & writing for the Minecraft Named Binary Tag (NBT) format,
created by Markus Petersson.

.. moduleauthor:: Tyler Kennedy <tk@tkte.ch>
"""
import gzip
from struct import unpack, pack


class BaseTag(object):
    def __init__(self, value, name=None):
        self.name = name
        self.value = value

    @staticmethod
    def _read_utf8(read):
        """Reads a length-prefixed UTF-8 string."""
        name_length = read('H', 2)[0]
        return read.io.read(name_length).decode('utf-8')

    @staticmethod
    def _write_utf8(write, value):
        """Writes a length-prefixed UTF-8 string."""
        write('h', len(value))
        write.io.write(value.encode('UTF-8'))

    @classmethod
    def read(cls, read, has_name=True):
        """
        Read the tag in using the reader `rd`.
        If `has_name` is `False`, skip reading the tag name.
        """
        name = cls._read_utf8(read) if has_name else None

        if cls is TAG_Compound:
            # A TAG_Compound is almost identical to Python's native dict()
            # object, or a Java HashMap.
            final = {}
            while True:
                # Find the type of each tag in a compound in turn.
                tag = read('b', 1)[0]
                if tag == 0:
                    # A tag of 0 means we've reached TAG_End, used to terminate
                    # a TAG_Compound.
                    break
                    # We read in each tag in turn, using its name as the key in
                # the dict (Since a compound cannot have repeating names,
                # this works fine).
                tmp = _tags[tag].read(read)
                final[tmp.name] = tmp
            return cls(final, name=name)
        elif cls is TAG_List:
            # A TAG_List is a very simple homogeneous array, similar to
            # Python's native list() object, but restricted to a single type.
            tag_type, length = read('bi', 5)
            tag_read = _tags[tag_type].read
            return cls(
                _tags[tag_type],
                [tag_read(read, has_name=False) for x in range(0, length)],
                name=name
            )
        elif cls is TAG_String:
            # A simple length-prefixed UTF-8 string.
            value = cls._read_utf8(read)
            return cls(value, name=name)
        elif cls is TAG_Byte_Array:
            # A simple array of (signed) bytes.
            length = read('i', 4)[0]
            return cls(read('{0}b'.format(length), length), name=name)
        elif cls is TAG_Int_Array:
            # A simple array of (signed) 4-byte integers.
            length = read('i', 4)[0]
            return cls(read('{0}i'.format(length), length * 4), name=name)
        elif cls is TAG_Byte:
            # A single (signed) byte.
            return cls(read('b', 1)[0], name=name)
        elif cls is TAG_Short:
            # A single (signed) short.
            return cls(read('h', 2)[0], name=name)
        elif cls is TAG_Int:
            # A signed (signed) 4-byte int.
            return cls(read('i', 4)[0], name=name)
        elif cls is TAG_Long:
            # A single (signed) 8-byte long.
            return cls(read('q', 8)[0], name=name)
        elif cls is TAG_Float:
            # A single single-precision floating point value.
            return cls(read('f', 4)[0], name=name)
        elif cls is TAG_Double:
            # A single double-precision floating point value.
            return cls(read('d', 8)[0], name=name)

    def write(self, write):
        # Only write the name TAG_String if our name is not `None`.
        # If you want a blank name, use ''.
        if self.name is not None:
            if isinstance(self, NBTFile):
                write('b', 0x0A)
            else:
                write('b', _tags.index(self.__class__))
            self._write_utf8(write, self.name)
        if isinstance(self, TAG_List):
            write('bi', _tags.index(self.type_), len(self.value))
            for item in self.value:
                # If our list item isn't of type self._type, convert
                # it before writing.
                if not isinstance(item, self.type_):
                    item = self.type_(item)
                item.write(write)
        elif isinstance(self, TAG_Compound):
            for v in self.value.values():
                v.write(write)
                # A tag of type 0 (TAg_End) terminates a TAG_Compound.
            write('b', 0)
        elif isinstance(self, TAG_String):
            self._write_utf8(write, self.value)
        elif isinstance(self, TAG_Int_Array):
            l = len(self.value)
            write('i{0}i'.format(l), l, *self.value)
        elif isinstance(self, TAG_Byte_Array):
            l = len(self.value)
            write('i{0}b'.format(l), l, *self.value)
        elif isinstance(self, TAG_Byte):
            write('b', self.value)
        elif isinstance(self, TAG_Short):
            write('h', self.value)
        elif isinstance(self, TAG_Int):
            write('i', self.value)
        elif isinstance(self, TAG_Long):
            write('q', self.value)
        elif isinstance(self, TAG_Float):
            write('f', self.value)
        elif isinstance(self, TAG_Double):
            write('d', self.value)

    def pretty(self, indent=0, indent_str='  '):
        """
        Pretty-print a tag in the same general style as Markus's example
        output.
        """
        return '{0}{1}({2!r}): {3!r}'.format(
            indent_str * indent,
            self.__class__.__name__,
            self.name,
            self.value
        )

    def __repr__(self):
        return '{0}({1!r}, {2!r})'.format(
            self.__class__.__name__, self.value, self.name)

    def __str__(self):
        return repr(self)

    def __unicode__(self):
        return unicode(repr(self), 'utf-8')


class TAG_Byte(BaseTag):
    pass


class TAG_Short(BaseTag):
    pass


class TAG_Int(BaseTag):
    pass


class TAG_Long(BaseTag):
    pass


class TAG_Float(BaseTag):
    pass


class TAG_Double(BaseTag):
    pass


class TAG_Byte_Array(BaseTag):
    def pretty(self, indent=0, indent_str='  '):
        return '{0}TAG_Byte_Array({1!r}): [{2} bytes]'.format(
            indent_str * indent, self.name, len(self.value))


class TAG_String(BaseTag):
    pass


class TAG_List(BaseTag, list):
    def __init__(self, tag_type, value=None, name=None):
        """
        Creates a new homogeneous list of `tag_type` items, copying `value`
        if provided.
        """
        self.name = name
        self.value = self
        self.type_ = tag_type
        if value is not None:
            self.extend(value)

    def pretty(self, indent=0, indent_str='  '):
        t = []
        t.append('{0}TAG_List({1!r}): {2} entries'.format(
            indent_str * indent, self.name, len(self.value)))
        t.append('{0}{{'.format(indent_str * indent))
        for v in self.value:
            t.append(v.pretty(indent + 1, indent_str))
        t.append('{0}}}'.format(indent_str * indent))
        return '\n'.join(t)

    def __repr__(self):
        return '{0}({1!r} entries, {2!r})'.format(
            self.__class__.__name__, len(self), self.name)


class TAG_Compound(BaseTag, dict):
    def __init__(self, value=None, name=None):
        self.name = name
        self.value = self
        if value is not None:
            self.update(value)

    def pretty(self, indent=0, indent_str='  '):
        t = []
        t.append('{0}TAG_Compound({1!r}): {2} entries'.format(
            indent_str * indent, self.name, len(self.value)))
        t.append('{0}{{'.format(indent_str * indent))
        for v in self.values():
            t.append(v.pretty(indent + 1, indent_str))
        t.append('{0}}}'.format(indent_str * indent))
        return '\n'.join(t)

    def __repr__(self):
        return '{0}({1!r} entries, {2!r})'.format(
            self.__class__.__name__, len(self), self.name)

    def __setitem__(self, key, value):
        """
        Sets the TAG_*'s name if it isn't already set to that of the key
        it's being assigned to. This results in cleaner code, as the name
        does not need to be specified twice.
        """
        if value.name is None:
            value.name = key
        super(TAG_Compound, self).__setitem__(key, value)

    def update(self, *args, **kwargs):
        """See `__setitem__`."""
        super(TAG_Compound, self).update(*args, **kwargs)
        for key, item in self.items():
            if item.name is None:
                item.name = key


class TAG_Int_Array(BaseTag):
    def pretty(self, indent=0, indent_str='  '):
        return '{0}TAG_Int_Array({1!r}): [{2} integers]'.format(
            indent_str * indent, self.name, len(self.value))

# The TAG_* types have the convienient property of being continuous.
# The code is written in such a way that if this were to no longer be
# true in the future, _tags can simply be replaced with a dict().
_tags = (
    None,
    TAG_Byte,
    TAG_Short,
    TAG_Int,
    TAG_Long,
    TAG_Float,
    TAG_Double,
    TAG_Byte_Array,
    TAG_String,
    TAG_List,
    TAG_Compound,
    TAG_Int_Array
    )


class NBTFile(TAG_Compound):
    class Compression(object):
        """
        Defines compression schemes to be used for loading and saving
        NBT files.
        """
        # NONE is simply for the sake of completeness.
        NONE = 10
        # Use Gzip compression when reading or writing.
        GZIP = 20

    def __init__(self, io=None, name=None, value=None, compression=None,
                 little_endian=False):
        """
        Creates a new NBTFile or loads one from any file-like object providing
        `read()`.

        Construction a new NBTFile() is as simple as:
        >>> nbt = NBTFile(name='')

        Whereas loading an existing one is most often done:
        >>> with open('my_file.nbt', rb') as io:
        ...     nbt = NBTFile(io=io, compression=NBTFile.Compression.GZIP)
        """
        # No file or path given, so we're creating a new NBTFile.
        if io is None:
            super(NBTFile, self).__init__(value if value else {}, name)
            return

        if compression is None or compression == NBTFile.Compression.NONE:
            final_io = io
        elif compression == NBTFile.Compression.GZIP:
            final_io = gzip.GzipFile(fileobj=io, mode='rb')
        else:
            raise ValueError('Unrecognized compression scheme.')

        # The pocket edition uses little-endian NBT files, but annoyingly
        # without any kind of header we can't determine that ourselves,
        # not even a magic number we could flip.
        if little_endian:
            read = lambda fmt, size: unpack('<' + fmt, final_io.read(size))
        else:
            read = lambda fmt, size: unpack('>' + fmt, final_io.read(size))
        read.io = final_io

        # All valid NBT files will begin with 0x0A, which is a TAG_Compound.
        if read('b', 1)[0] != 0x0A:
            raise IOError('NBTFile does not begin with 0x0A.')

        tmp = TAG_Compound.read(read)
        super(NBTFile, self).__init__(tmp, tmp.name)

    def save(self, io, compression=None, little_endian=False):
        """
        Saves the `NBTFile()` to `io`, which can be any file-like object
        providing `write()`.
        """
        if compression is None or compression == NBTFile.Compression.NONE:
            final_io = io
        elif compression == NBTFile.Compression.GZIP:
            final_io = gzip.GzipFile(fileobj=io, mode='wb')

        if little_endian:
            write = lambda fmt, *args: final_io.write(pack('<' + fmt, *args))
        else:
            write = lambda fmt, *args: final_io.write(pack('>' + fmt, *args))
        write.io = final_io

        self.write(write)
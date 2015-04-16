"""
Contains the datatypes used by the networking part of `pyminecraft`.
The types are described at http://wiki.vg/Protocol#Data_types

These datatypes are used by the packet definitions.
"""

__all__ = ["ENDIANNESS",
           "Datatype", "NumberDatatype", "StringDatatype",
           "Boolean",
           "Byte", "UnsignedByte",
           "Short", "UnsignedShort",
           "Integer", "UnsignedInteger",
           "Long", "UnsignedLong",
           "LongLong", "UnsignedLongLong",
           "Float",
           "Double",
           "VarInt", "VarLong",
           "String"]

from minecraft.exceptions import DeserializationError, SerializationError
from minecraft.compat import long
from io import BytesIO
import struct
import collections

ENDIANNESS = "!"  # Network, big-endian


class Datatype(object):
    """
    Base object for all `pyminecraft` networking datatypes.


    .. note::
        If ``ALLOWED_SERIALIZATION_TYPES`` is not empty, only the types found
        in ``ALLOWED_SERIALIZATION_TYPES`` are allowed as serialization
        ``data``. This does somewhat go against the Duck-typing principle.

        The same applies for ``ALLOWED_DESERIALIZATION_TYPES``.

    .. note::
        If ``DISALLOWED_SERIALIZATION_TYPES`` is not empty, only the types
        found in ``DISALLOWED_SERIALIZATION_TYPES`` are allowed as
        serialization ``data``. This does somewhat go against the
        Duck-typing principle.

        ``DISALLOWED_SERIALIZATION_TYPES`` exists as a way to exclude certain
        subclasses of a given type.

        The same applies for ``DISALLOWED_DESERIALIZATION_TYPES``.
    """
    FORMAT = ""
    SIZE = 0

    ALLOWED_SERIALIZATION_TYPES = tuple()
    ALLOWED_DESERIALIZATION_TYPES = tuple()

    DISALLOWED_SERIALIZATION_TYPES = tuple()
    DISALLOWED_SERIALIZATION_TYPES = tuple()

    @classmethod
    def read(cls, fileobject):
        bin_data = fileobject.read(cls.SIZE)
        return cls.deserialize(bin_data)

    @classmethod
    def deserialize(cls, data):
        cls.raise_deserialization_data(data)

        deserialized_data = struct.unpack(ENDIANNESS + cls.FORMAT, data)[0]
        return deserialized_data

    @classmethod
    def write(cls, fileobject, data):
        return fileobject.write(cls.serialize(data))

    @classmethod
    def serialize(cls, data):
        cls.raise_serialization_data(data)

        serialized_data = struct.pack(ENDIANNESS + cls.FORMAT, data)
        return serialized_data

    @classmethod
    def raise_serialization_data(cls, data):
        """
        Raises an appropriate ``Exception`` if ``data`` is not valid.

        :return: ``None``
        :rtype: ``None``
        :raises: ``TypeError``, ``ValueError``
        """
        error_message = "'data's type ('{}') is not an allowed type."
        error_message = error_message.format(type(data).__name__)

        if (cls.ALLOWED_SERIALIZATION_TYPES and
            not any([isinstance(data, type_) for type_
                    in cls.ALLOWED_SERIALIZATION_TYPES])):

            raise TypeError(error_message)

        for type_ in cls.DISALLOWED_SERIALIZATION_TYPES:
            if isinstance(data, type_):
                raise TypeError(error_message)

        cls._raise_serialization_value_error_data(data)

        return None

    @classmethod
    def _raise_serialization_value_error_data(cls, data):
        """
        Raises a ValueError if ``data`` is not valid.

        :return: ``None``
        :rtype: ``None``
        :raises: ``ValueError``
        """
        return None

    @classmethod
    def raise_deserialization_data(cls, data):
        """
        Raises an appropriate ``Exception`` if ``data`` is not valid.

        :return: ``None``
        :rtype: ``None``
        :raises: ``TypeError``, ``ValueError``
        """
        if (cls.ALLOWED_DESERIALIZATION_TYPES and
            not any([isinstance(data, type_) for type_
                    in cls.ALLOWED_DESERIALIZATION_TYPES])):

            err = "'data's type ('{}') is not an allowed type."
            err = err.format(type(data).__name__)

            raise TypeError(err)

        if cls.SIZE != len(data):
            err = "'data' must have a length of {}, not {}"
            err = err.format(str(cls.SIZE), str(len(data)))

            raise ValueError(err)

        return None


class NumberDatatype(Datatype):
    """
    Base abstract class for all number-like minecraft networking datatypes.

    .. note::
        Numbers to be serialized must be between this classes
        ``MIN_NUMBER_VALUE`` and ``MAX_NUMBER_VALUE``, or a ``ValueError`` will
        be raised.

        If ``MIN_NUMBER_VALUE`` or ``MAX_NUMBER_VALUE`` are ``None``
        (as in the case of float), checking is left to the ``struct`` module.
    """

    MIN_NUMBER_VALUE = None
    MAX_NUMBER_VALUE = None

    ALLOWED_SERIALIZATION_TYPES = (int, long)
    DISALLOWED_SERIALIZATION_TYPES = (bool,)

    @classmethod
    def _raise_serialization_value_error_data(cls, data):
        if (cls.MIN_NUMBER_VALUE is not None
                and cls.MAX_NUMBER_VALUE is not None):

            if not cls.MIN_NUMBER_VALUE <= data <= cls.MAX_NUMBER_VALUE:
                err = "'data' must be an integer with value between {} and {}."
                err = err.format(str(cls.MIN_NUMBER_VALUE),
                                 str(cls.MAX_NUMBER_VALUE))

                raise ValueError(err)

        return None


class StringDatatype(Datatype):
    pass


class Boolean(Datatype):
    FORMAT = "?"
    SIZE = 1

    ALLOWED_SERIALIZATION_TYPES = (bool,)
    ALLOWED_DESERIALIZATION_TYPES = (collections.Sequence,)


class Byte(NumberDatatype):
    FORMAT = "b"
    SIZE = 1

    MIN_NUMBER_VALUE = -128
    MAX_NUMBER_VALUE = 127


class UnsignedByte(NumberDatatype):
    FORMAT = "B"
    SIZE = 1

    MIN_NUMBER_VALUE = 0
    MAX_NUMBER_VALUE = 255


class Short(NumberDatatype):
    FORMAT = "h"
    SIZE = 2

    MIN_NUMBER_VALUE = -32768
    MAX_NUMBER_VALUE = 32767


class UnsignedShort(NumberDatatype):
    FORMAT = "H"
    SIZE = 2

    MIN_NUMBER_VALUE = 0
    MAX_NUMBER_VALUE = 65535


class Integer(NumberDatatype):
    FORMAT = "i"
    SIZE = 4

    MIN_NUMBER_VALUE = -2147483648
    MAX_NUMBER_VALUE = 2147483647


class UnsignedInteger(NumberDatatype):
    FORMAT = "I"
    SIZE = 4

    MIN_NUMBER_VALUE = 0
    MAX_NUMBER_VALUE = 4294967295


class Long(NumberDatatype):
    FORMAT = "l"
    SIZE = 4

    MIN_NUMBER_VALUE = -2147483648
    MAX_NUMBER_VALUE = 2147483647


class UnsignedLong(NumberDatatype):
    FORMAT = "L"
    SIZE = 4

    MIN_NUMBER_VALUE = 0
    MAX_NUMBER_VALUE = 4294967295


class LongLong(NumberDatatype):
    FORMAT = "q"
    SIZE = 8

    MIN_NUMBER_VALUE = -9223372036854775808
    MAX_NUMBER_VALUE = 9223372036854775807


class UnsignedLongLong(NumberDatatype):
    FORMAT = "Q"
    SIZE = 8

    MIN_NUMBER_VALUE = 0
    MAX_NUMBER_VALUE = 18446744073709551615


class Float(NumberDatatype):
    FORMAT = "f"
    SIZE = 4


class Double(NumberDatatype):
    FORMAT = "d"
    SIZE = 8


class VarInt(NumberDatatype):
    # See: https://developers.google.com/protocol-buffers/docs/encoding#varints
    # See: https://github.com/ammaraskar/pyCraft/blob/7e8df473520d57ca22fb57888681f51705128cdc/network/types.py#l123  # noqa
    # See: https://github.com/google/protobuf/blob/0c59f2e6fc0a2cb8e8e3b4c7327f650e8586880a/python/google/protobuf/internal/decoder.py#l107  # noqa
    # According to http://wiki.vg/Protocol#Data_types,
    # MineCraftian VarInts can be at most 5 bytes.

    # Maximum integer value: size of serialized VarInt in bytes
    SIZE_TABLE = {
        2**7: 1,
        2**14: 2,
        2**21: 3,
        2**28: 4,
        2**35: 5,
    }

    # Largest element in SIZE_TABLE, assuming largest element is last.
    MAX_SIZE = list(SIZE_TABLE.items())[-1][-1]

    @classmethod
    def read(cls, fileobject):
        number = 0  # The decoded number

        i = 0  # Incrementor
        while True:
            if i > cls.MAX_SIZE:  # Check if we have exceeded max-size
                name_of_self = str(type(cls))
                e = "Data too large to be a {}".format(name_of_self)
                raise DeserializationError(e)

            try:
                byte = ord(fileobject.read(1))  # Read a byte as integer
            except TypeError:
                e = "Fileobject ran out of data. Socket closed?"
                raise DeserializationError(e)

            number |= ((byte & 0x7f) << (i * 7))
            if not (byte & 0x80):
                break

            i += 1
        return number

    @classmethod
    def deserialize(cls, data):
        data_fileobject = BytesIO(bytes(data))
        return cls.read(data_fileobject)

    @classmethod
    def serialize(cls, data):
        if data > cls.SIZE_TABLE[-1][0]:
            name_of_self = str(type(cls))
            e = "Number too big to serialize as {}".format(name_of_self)
            raise SerializationError(e)

        result = bytes()  # Where we store the serialized number

        while True:
            byte = data & 0x7f
            data >>= 7

            result += UnsignedByte.serialize(byte | (0x80 if data > 0 else 0))

            if not data:
                break

        return result


class VarLong(VarInt):
    # According to http://wiki.vg/Protocol#Data_types,
    # MineCraftian VarInts can be at most 10 bytes.
    SIZE_TABLE = VarInt.SIZE_TABLE
    SIZE_TABLE.update(
        {
            2**42: 6,
            2**49: 7,
            2**56: 8,
            2**63: 9,
            2**70: 10,
        }
    )

    MAX_SIZE = list(SIZE_TABLE.items())[-1][-1]


class String(Datatype):
    FORMAT = "utf-8"

    @classmethod
    def read(cls, fileobject):
        str_size = VarInt.read(fileobject)
        string = fileobject.read(str_size).decode(cls.FORMAT)

        return string

    @classmethod
    def deserialize(cls, data):
        data_fileobject = BytesIO(bytes(data))
        return cls.read(data_fileobject)

    @classmethod
    def serialize(cls, data):
        data = data.encode(cls.FORMAT)
        len_data = VarInt.serialize(len(data))

        return len_data + data

"""Contains definitions for minecraft's different data types
Each type has a method which is used to read and write it.
These definitions and methods are used by the packet definitions
"""
from __future__ import division
import struct
import uuid

from .utility import Vector


__all__ = (
    'Type', 'Boolean', 'UnsignedByte', 'Byte', 'Short', 'UnsignedShort',
    'Integer', 'FixedPointInteger', 'Angle', 'VarInt', 'Long',
    'UnsignedLong', 'Float', 'Double', 'ShortPrefixedByteArray',
    'VarIntPrefixedByteArray', 'TrailingByteArray', 'String', 'UUID',
    'Position',
)


class Type(object):
    __slots__ = ()

    @classmethod
    def read_with_context(cls, file_object, _context):
        return cls.read(file_object)

    @classmethod
    def send_with_context(cls, value, socket, _context):
        return cls.send(value, socket)

    @classmethod
    def read(cls, file_object):
        if cls.read_with_context == Type.read_with_context:
            raise NotImplementedError('One of "read" or "read_with_context" '
                                      'must be overridden in a subclass.')
        else:
            raise TypeError('This type requires a ConnectionContext: '
                            'call "read_with_context" instead of "read".')

    @classmethod
    def send(cls, value, socket):
        if cls.send_with_context == Type.send_with_context:
            raise NotImplementedError('One of "send" or "send_with_context" '
                                      'must be overridden in a subclass.')
        else:
            raise TypeError('This type requires a ConnectionContext: '
                            'call "send_with_context" instead of "send".')


class Boolean(Type):
    @staticmethod
    def read(file_object):
        return struct.unpack('?', file_object.read(1))[0]

    @staticmethod
    def send(value, socket):
        socket.send(struct.pack('?', value))


class UnsignedByte(Type):
    @staticmethod
    def read(file_object):
        return struct.unpack('>B', file_object.read(1))[0]

    @staticmethod
    def send(value, socket):
        socket.send(struct.pack('>B', value))


class Byte(Type):
    @staticmethod
    def read(file_object):
        return struct.unpack('>b', file_object.read(1))[0]

    @staticmethod
    def send(value, socket):
        socket.send(struct.pack('>b', value))


class Short(Type):
    @staticmethod
    def read(file_object):
        return struct.unpack('>h', file_object.read(2))[0]

    @staticmethod
    def send(value, socket):
        socket.send(struct.pack('>h', value))


class UnsignedShort(Type):
    @staticmethod
    def read(file_object):
        return struct.unpack('>H', file_object.read(2))[0]

    @staticmethod
    def send(value, socket):
        socket.send(struct.pack('>H', value))


class Integer(Type):
    @staticmethod
    def read(file_object):
        return struct.unpack('>i', file_object.read(4))[0]

    @staticmethod
    def send(value, socket):
        socket.send(struct.pack('>i', value))


class FixedPointInteger(Type):
    @staticmethod
    def read(file_object):
        return Integer.read(file_object) / 32

    @staticmethod
    def send(value, socket):
        Integer.send(int(value * 32), socket)


class Angle(Type):
    @staticmethod
    def read(file_object):
        # Linearly transform angle in steps of 1/256 into steps of 1/360
        return 360 * UnsignedByte.read(file_object) / 256

    @staticmethod
    def send(value, socket):
        # Normalize angle between 0 and 255 and convert to int.
        UnsignedByte.send(round(256 * ((value % 360) / 360)), socket)


class VarInt(Type):
    @staticmethod
    def read(file_object):
        number = 0
        # Limit of 5 bytes, otherwise its possible to cause
        # a DOS attack by sending VarInts that just keep
        # going
        bytes_encountered = 0
        while True:
            byte = file_object.read(1)
            if len(byte) < 1:
                raise EOFError("Unexpected end of message.")

            byte = ord(byte)
            number |= (byte & 0x7F) << 7 * bytes_encountered
            if not byte & 0x80:
                break

            bytes_encountered += 1
            if bytes_encountered > 5:
                raise ValueError("Tried to read too long of a VarInt")
        return number

    @staticmethod
    def send(value, socket):
        out = bytes()
        while True:
            byte = value & 0x7F
            value >>= 7
            out += struct.pack("B", byte | (0x80 if value > 0 else 0))
            if value == 0:
                break
        socket.send(out)

    @staticmethod
    def size(value):
        for max_value, size in VARINT_SIZE_TABLE.items():
            if value < max_value:
                return size
        raise ValueError("Integer too large")


# Maps (maximum integer value -> size of VarInt in bytes)
VARINT_SIZE_TABLE = {
    2 ** 7: 1,
    2 ** 14: 2,
    2 ** 21: 3,
    2 ** 28: 4,
    2 ** 35: 5,
    2 ** 42: 6,
    2 ** 49: 7,
    2 ** 56: 8,
    2 ** 63: 9,
    2 ** 70: 10,
    2 ** 77: 11,
    2 ** 84: 12
}


class Long(Type):
    @staticmethod
    def read(file_object):
        return struct.unpack('>q', file_object.read(8))[0]

    @staticmethod
    def send(value, socket):
        socket.send(struct.pack('>q', value))


class UnsignedLong(Type):
    @staticmethod
    def read(file_object):
        return struct.unpack('>Q', file_object.read(8))[0]

    @staticmethod
    def send(value, socket):
        socket.send(struct.pack('>Q', value))


class Float(Type):
    @staticmethod
    def read(file_object):
        return struct.unpack('>f', file_object.read(4))[0]

    @staticmethod
    def send(value, socket):
        socket.send(struct.pack('>f', value))


class Double(Type):
    @staticmethod
    def read(file_object):
        return struct.unpack('>d', file_object.read(8))[0]

    @staticmethod
    def send(value, socket):
        socket.send(struct.pack('>d', value))


class ShortPrefixedByteArray(Type):
    @staticmethod
    def read(file_object):
        length = Short.read(file_object)
        return struct.unpack(str(length) + "s", file_object.read(length))[0]

    @staticmethod
    def send(value, socket):
        Short.send(len(value), socket)
        socket.send(value)


class VarIntPrefixedByteArray(Type):
    @staticmethod
    def read(file_object):
        length = VarInt.read(file_object)
        return struct.unpack(str(length) + "s", file_object.read(length))[0]

    @staticmethod
    def send(value, socket):
        VarInt.send(len(value), socket)
        socket.send(struct.pack(str(len(value)) + "s", value))


class TrailingByteArray(Type):
    """ A byte array consisting of all remaining data. If present in a packet
        definition, this should only be the type of the last field. """

    @staticmethod
    def read(file_object):
        return file_object.read()

    @staticmethod
    def send(value, socket):
        socket.send(value)


class String(Type):
    @staticmethod
    def read(file_object):
        length = VarInt.read(file_object)
        return file_object.read(length).decode("utf-8")

    @staticmethod
    def send(value, socket):
        value = value.encode('utf-8')
        VarInt.send(len(value), socket)
        socket.send(value)


class UUID(Type):
    @staticmethod
    def read(file_object):
        return str(uuid.UUID(bytes=file_object.read(16)))

    @staticmethod
    def send(value, socket):
        socket.send(uuid.UUID(value).bytes)


class Position(Type, Vector):
    """3D position vectors with a specific, compact network representation."""
    __slots__ = ()

    @staticmethod
    def read_with_context(file_object, context):
        location = UnsignedLong.read(file_object)
        x = int(location >> 38)                # 26 most significant bits

        if context.protocol_version >= 443:
            z = int((location >> 12) & 0x3FFFFFF)  # 26 intermediate bits
            y = int(location & 0xFFF)              # 12 least signficant bits
        else:
            y = int((location >> 26) & 0xFFF)      # 12 intermediate bits
            z = int(location & 0x3FFFFFF)          # 26 least significant bits

        if x >= pow(2, 25):
            x -= pow(2, 26)

        if y >= pow(2, 11):
            y -= pow(2, 12)

        if z >= pow(2, 25):
            z -= pow(2, 26)

        return Position(x=x, y=y, z=z)

    @staticmethod
    def send_with_context(position, socket, context):
        # 'position' can be either a tuple or Position object.
        x, y, z = position
        value = ((x & 0x3FFFFFF) << 38 | (z & 0x3FFFFFF) << 12 | (y & 0xFFF)
                 if context.protocol_version >= 443 else
                 (x & 0x3FFFFFF) << 38 | (y & 0xFFF) << 26 | (z & 0x3FFFFFF))
        UnsignedLong.send(value, socket)

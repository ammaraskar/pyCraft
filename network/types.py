"""Contains definitions for minecraft's different data types
Each type has a method which is used to read and write it.
These definitions and methods are used by the packet definitions
"""
import struct


class Type(object):
    @staticmethod
    def read(file_object):
        pass

    @staticmethod
    def send(value, socket):
        pass


# =========================================================


class Boolean(Type):
    @staticmethod
    def read(file_object):
        return struct.unpack('?', file_object.read(1))[0]

    @staticmethod
    def send(value, socket):
        socket.send(struct.pack('?', value))


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


class VarInt(Type):
    @staticmethod
    def read_socket(s):
        d = 0
        for i in range(5):
            b = s.recv(1)
            if b == "":
                raise RuntimeError("Socket disconnected")
            b = ord(b)
            d |= (b & 0x7F) << 7 * i
            if not b & 0x80:
                break
        return d

    @staticmethod
    def read(file_object):
        d = 0
        for i in range(5):
            b = ord(file_object.read(1))
            d |= (b & 0x7F) << 7 * i
            if not b & 0x80:
                break
        return d

    @staticmethod
    def send(value, socket):
        o = ""
        while True:
            b = value & 0x7F
            value >>= 7
            o += struct.pack("B", b | (0x80 if value > 0 else 0))
            if value == 0:
                break
        socket.send(o)


class Long(Type):
    @staticmethod
    def read(file_object):
        return struct.unpack('>q', file_object.read(8))[0]

    @staticmethod
    def send(value, socket):
        socket.send(struct.pack('>q', value))


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


class ByteArray(Type):
    @staticmethod
    def read(file_object, length=None):
        if length is None:
            length = Short.read(file_object)
        return struct.unpack(str(length) + "s", file_object.read(length))[0]

    @staticmethod
    def send(value, socket):
        Short.send(len(value), socket)
        socket.send(value)


class String(Type):
    @staticmethod
    def read(file_object):
        length = VarInt.read(file_object)
        return unicode(file_object.read(length), "utf-8")

    @staticmethod
    def send(value, socket):
        value = unicode(value).encode('utf-8')
        VarInt.send(len(value), socket)
        socket.send(value)

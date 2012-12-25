import struct
import types
from io import BytesIO
from pynbt import NBTFile

def readBoolean(FileObject):
    return struct.unpack('?', FileObject.read(1))[0]


def readByte(FileObject):
    return struct.unpack('>b', FileObject.read(1))[0]


def readUnsignedByte(FileObject):
    return struct.unpack('>B', FileObject.read(1))[0]


def readShort(FileObject):
    return struct.unpack('>h', FileObject.read(2))[0]


def readUnsignedShort(FileObject):
    return struct.unpack('>H', FileObject.read(2))[0]


def readInt(FileObject):
    return struct.unpack('>i', FileObject.read(4))[0]


def readFloat(FileObject):
    return struct.unpack('>f', FileObject.read(4))[0]


def readLong(FileObject):
    return struct.unpack('>q', FileObject.read(8))[0]


def readDouble(FileObject):
    return struct.unpack('>d', FileObject.read(8))[0]


def readByteArray(FileObject, length):
    return struct.unpack(str(length) + "s", FileObject.read(length))[0]


def readString(FileObject):
    length = readShort(FileObject) * 2
    return FileObject.read(length).decode("utf-16be")


def sendBoolean(socket, value):
    assert type(value) is types.BooleanType, "value is not a boolean: %r" % value
    socket.send(struct.pack('?', value))


def sendByte(socket, value):
    socket.send(struct.pack('>b', value))


def sendUnsignedByte(socket, value):
    socket.send(struct.pack('>B', value))


def sendShort(socket, value):
    socket.send(struct.pack('>h', value))


def sendUnsignedShort(socket, value):
    socket.send(struct.pack('>H', value))


def sendInt(socket, value):
    assert type(value) is types.IntType, "value is not an integer: %r" % value
    socket.send(struct.pack('>i', value))


def sendFloat(socket, value):
    socket.send(struct.pack('>f', value))


def sendLong(socket, value):
    socket.send(struct.pack('>q', value))


def sendDouble(socket, value):
    socket.send(struct.pack('>d', value))


def sendString(socket, value):
    if (type(value) is not types.StringType):
        value = str(value)
    socket.send(struct.pack('>h', value.__len__()))
    socket.send(value.encode('utf-16be'))


def readEntityMetadata(FileObject):
    metadata = {}
    byte = readUnsignedByte(FileObject)
    while byte != 127:
        index = byte & 0x1F # Lower 5 bits
        ty = byte >> 5   # Upper 3 bits
        if ty == 0: val = readByte(FileObject)
        if ty == 1: val = readShort(FileObject)
        if ty == 2: val = readInt(FileObject)
        if ty == 3: val = readFloat(FileObject)
        if ty == 4:
            val = readString(FileObject)
        if ty == 5:
            val = {}
            val["id"] = readShort(FileObject)
            if (val["id"] != -1):
                val["count"] = readByte(FileObject)
                val["damage"] = readShort(FileObject)
                nbtDataLength = readShort(FileObject)
                if (nbtDataLength != -1):
                    val["NBT"] = NBTFile(BytesIO(readByteArray(FileObject, nbtDataLength)),
                        compression=NBTFile.Compression.GZIP)
        if ty == 6:
            val = []
            for i in range(3):
                val.append(readInt(FileObject))
        metadata[index] = (ty, val)
        byte = readUnsignedByte(FileObject)
    return metadata


def readSlotData(FileObject):
    BlockID = readShort(FileObject)
    if (BlockID != -1):
        ItemCount = readByte(FileObject)
        Damage = readShort(FileObject)
        MetadataLength = readShort(FileObject)
        if (MetadataLength != -1):
            ByteArray = readByteArray(FileObject, MetadataLength)
            NBTData = NBTFile(BytesIO(ByteArray), compression=NBTFile.Compression.GZIP)
            return {'BlockID': BlockID,
                    'ItemCount': ItemCount,
                    'Damage': Damage,
                    'Data': NBTData
            }
        return {'BlockID': BlockID,
                'ItemCount': ItemCount,
                'Damage': Damage
        }
    return {'BlockID': -1,
            'ItemCount': 0
    }
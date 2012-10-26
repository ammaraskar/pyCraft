import struct

def readBoolean(FileObject):
    return struct.unpack('?', FileObject.read(1))[0]

def readByte(FileObject):
    return struct.unpack('!b', FileObject.read(1))[0]

def readUnsignedByte(FileObject):
    return struct.unpack('!B', FileObject.read(1))[0]

def readShort(FileObject):
    return struct.unpack('!h', FileObject.read(2))[0]

def readUnsignedShort(FileObject):
    return struct.unpack('!H', FileObject.read(2))[0]

def readInt(FileObject):
    return struct.unpack('!i', FileObject.read(4))[0]

def readFloat(FileObject):
    return struct.unpack('!f', FileObject.read(4))[0]

def readLong(FileObject):
    return struct.unpack('!q', FileObject.read(8))[0]

def readDouble(FileObject):
    return struct.unpack('!d', FileObject.read(8))[0]

def readByteArray(FileObject, length):
    return struct.unpack(str(length) + "s", FileObject.read(length))[0]

def readString(FileObject):
    length = readShort(FileObject) * 2
    return FileObject.read(length).decode("utf-16be")

def readEntityMetadata(FileObject):
    metadata = {}
    byte = struct.unpack('!B', FileObject.read(1))[0]
    while byte != 127:
        index = byte & 0x1F # Lower 5 bits
        ty    = byte >> 5   # Upper 3 bits
        if ty == 0: val = struct.unpack('!b', FileObject.read(1))[0]
        if ty == 1: val = struct.unpack('!h', FileObject.read(2))[0]
        if ty == 2: val = readInt(FileObject)
        if ty == 3: val = struct.unpack('!f', FileObject.read(4))[0] 
        if ty == 4: 
            length = struct.unpack('!h', FileObject.read(2))[0] * 2
            val = FileObject.read(length).decode('utf-16be')
        if ty == 5:
            val = {}
            val["id"]     = struct.unpack('!h', FileObject.read(2))[0]
            if (val["id"] != -1):
                val["count"]  = struct.unpack('!b', FileObject.read(1))[0]
                val["damage"] = struct.unpack('!h', FileObject.read(2))[0]
        if ty == 6:
            val = []
            for i in range(3):
                val.append(readInt(FileObject))
        metadata[index] = (ty, val)
        byte = struct.unpack('!B', FileObject.read(1))[0]
    return metadata

def readSlotData(FileObject):
    BlockID = struct.unpack('!h', FileObject.read(2))[0]
    if(BlockID != -1):
        ItemCount = struct.unpack('!b', FileObject.read(1))[0]
        Damage = struct.unpack('!h', FileObject.read(2))[0]
        MetadataLength = struct.unpack('!h', FileObject.read(2))[0]
        if(MetadataLength != -1):
            raw = FileObject.read(MetadataLength)
            ByteArray = struct.unpack(str(MetadataLength) + "s", raw)[0]
            return {'BlockID' : BlockID,
                    'ItemCount' : ItemCount,
                    'Damage' : Damage,
                    'Data' : ByteArray
                    }
        return {'BlockID' : BlockID,
                'ItemCount' : ItemCount,
                'Damage' : Damage
                }
    return {'BlockID' : -1,
            'ItemCount' : 0
            }
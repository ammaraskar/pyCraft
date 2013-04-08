import DataUtil
import PacketSenderManager
from io import BytesIO
from pynbt import NBTFile

def handle00(FileObject, socket):
    KAid = DataUtil.readInt(FileObject)
    PacketSenderManager.send00(socket, KAid)


def handle01(FileObject):
    Eid = DataUtil.readInt(FileObject)
    world = DataUtil.readString(FileObject)
    mode = DataUtil.readByte(FileObject)
    dimension = DataUtil.readByte(FileObject)
    difficulty = DataUtil.readByte(FileObject)
    FileObject.read(1)
    maxplayers = DataUtil.readByte(FileObject)
    return {'EntityID': Eid,
            'World': world,
            'Mode': mode,
            'Dimension': dimension,
            'Difficulty': difficulty,
            'MaxPlayers': maxplayers
    }


def handle02(FileObject):
    message = DataUtil.readString(FileObject)
    return message


def handle03(FileObject):
    message = DataUtil.readString(FileObject)
    return {'Message': message}


def handle04(FileObject):
    time = DataUtil.readLong(FileObject)
    dayTime = DataUtil.readLong(FileObject)
    return {'Time': time,
            'DayTime': dayTime
    }


def handle05(FileObject):
    EntityID = DataUtil.readInt(FileObject)
    Slot = DataUtil.readShort(FileObject)
    Item = DataUtil.readSlotData(FileObject)
    return {'EntityID': EntityID,
            'Slot': Slot,
            'Item': Item
    }


def handle06(FileObject):
    x = DataUtil.readInt(FileObject)
    y = DataUtil.readInt(FileObject)
    z = DataUtil.readInt(FileObject)
    return {'x': x,
            'y': y,
            'z': z
    }


def handle07(FileObject):
    userID = DataUtil.readInt(FileObject)
    targetID = DataUtil.readInt(FileObject)
    mButton = DataUtil.readBoolean(FileObject)
    return {'userID': userID,
            'targetID': targetID,
            'mButton': mButton
    }


def handle08(FileObject):
    health = DataUtil.readShort(FileObject)
    food = DataUtil.readShort(FileObject)
    saturation = DataUtil.readFloat(FileObject)
    return {'health': health,
            'food': food,
            'saturation': saturation
    }


def handle09(FileObject):
    dimension = DataUtil.readInt(FileObject)
    difficulty = DataUtil.readByte(FileObject)
    mode = DataUtil.readByte(FileObject)
    height = DataUtil.readShort(FileObject)
    world = DataUtil.readString(FileObject)
    return {'Dimension': dimension,
            'Difficulty': difficulty,
            'Mode': mode,
            'Height': height,
            'World': world
    }


def handle0D(FileObject):
    x = DataUtil.readDouble(FileObject)
    stance = DataUtil.readDouble(FileObject)
    y = DataUtil.readDouble(FileObject)
    z = DataUtil.readDouble(FileObject)
    yaw = DataUtil.readFloat(FileObject)
    pitch = DataUtil.readFloat(FileObject)
    onGround = DataUtil.readBoolean(FileObject)
    return {'x': x,
            'stance': stance,
            'y': y,
            'z': z,
            'yaw': yaw,
            'pitch': pitch,
            'onGround': onGround
    }


def handle10(FileObject):
    slotID = DataUtil.readShort(FileObject)
    return {'SlotID': slotID}


def handle11(FileObject):
    EntityID = DataUtil.readInt(FileObject)
    FileObject.read(1) #Unused
    x = DataUtil.readInt(FileObject)
    y = DataUtil.readByte(FileObject)
    z = DataUtil.readInt(FileObject)
    return {'EntityID': EntityID,
            'x': x,
            'y': y,
            'z': z
    }


def handle12(FileObject):
    EntityID = DataUtil.readInt(FileObject)
    Animation = DataUtil.readByte(FileObject)
    return {'EntityID': EntityID,
            'AnimationID': Animation
    }


def handle14(FileObject):
    EntityID = DataUtil.readInt(FileObject)
    PlayerName = DataUtil.readString(FileObject)
    x = DataUtil.readInt(FileObject)
    y = DataUtil.readInt(FileObject)
    z = DataUtil.readInt(FileObject)
    yaw = DataUtil.readFloat(FileObject)
    pitch = DataUtil.readFloat(FileObject)
    curItem = DataUtil.readShort(FileObject)
    metadata = DataUtil.readEntityMetadata(FileObject)
    toReturn = {'EntityID': EntityID,
                'Player Name': PlayerName,
                'x': x,
                'y': y,
                'z': z,
                'yaw': yaw,
                'pitch': pitch,
                'curItem': curItem,
                'Metadata': metadata
    }
    return toReturn


def handle15(FileObject):
    EntityID = DataUtil.readInt(FileObject)
    ItemID = DataUtil.readShort(FileObject)
    if (ItemID != -1):
        Count = DataUtil.readByte(FileObject)
        Damage = DataUtil.readShort(FileObject)
        ArrayLength = DataUtil.readShort(FileObject)
        if (ArrayLength != -1):
            Array = FileObject.read(ArrayLength) #TODO: find out what this does and do stuff accrodingly
    x = DataUtil.readInt(FileObject)
    y = DataUtil.readInt(FileObject)
    z = DataUtil.readInt(FileObject)
    Rotation = DataUtil.readByte(FileObject)
    Pitch = DataUtil.readByte(FileObject)
    Roll = DataUtil.readByte(FileObject)
    toReturn = {'EntityID': EntityID,
                'ItemID': ItemID,
                'x': x,
                'y': y,
                'z': z,
                'Rotation': Rotation,
                'Pitch': Pitch,
                'Roll': Roll
    }
    if (ItemID != -1):
        toReturn['Count'] = Count
        toReturn['Damage'] = Damage
    return toReturn


def handle16(FileObject):
    CollectedID = DataUtil.readInt(FileObject)
    CollectorID = DataUtil.readInt(FileObject)
    return {'CollectedID': CollectedID,
            'CollectorID': CollectorID
    }


def handle17(FileObject):
    EntityID = DataUtil.readInt(FileObject)
    Type = DataUtil.readByte(FileObject)
    x = DataUtil.readInt(FileObject)
    y = DataUtil.readInt(FileObject)
    z = DataUtil.readInt(FileObject)
    yaw = DataUtil.readByte(FileObject)
    pitch = DataUtil.readByte(FileObject)
    data = DataUtil.readInt(FileObject)
    if (data > 0):
        SpeedX = DataUtil.readShort(FileObject)
        SpeedY = DataUtil.readShort(FileObject)
        SpeedZ = DataUtil.readShort(FileObject)
        return {'EntityID': EntityID,
                'Type': Type,
                'x': x,
                'y': y,
                'z': z,
                'yaw': yaw,
                'pitch': pitch,
                'SpeedX': SpeedX,
                'SpeedY': SpeedY,
                'SpeedZ': SpeedZ
        }
    else:
        return {'EntityID': EntityID,
                'Type': Type,
                'x': x,
                'y': y,
                'z': z,
                'yaw': yaw,
                'pitch': pitch
        }


def handle18(FileObject):
    EntityID = DataUtil.readInt(FileObject)
    Type = DataUtil.readByte(FileObject)
    x = DataUtil.readInt(FileObject)
    y = DataUtil.readInt(FileObject)
    z = DataUtil.readInt(FileObject)
    Yaw = DataUtil.readByte(FileObject)
    Pitch = DataUtil.readByte(FileObject)
    HeadYaw = DataUtil.readByte(FileObject)
    VelocityX = DataUtil.readShort(FileObject)
    VelocityY = DataUtil.readShort(FileObject)
    VelocityZ = DataUtil.readShort(FileObject)
    metadata = DataUtil.readEntityMetadata(FileObject)

    return {'EntityID': EntityID,
            'Type': Type,
            'x': x,
            'y': y,
            'z': z,
            'Yaw': Yaw,
            'Pitch': Pitch,
            'HeadYaw': HeadYaw,
            'Metadata': metadata,
            'VelocityX': VelocityX,
            'VelocityY': VelocityY,
            'VelocityZ': VelocityZ
    }


def handle19(FileObject):
    EntityID = DataUtil.readInt(FileObject)
    Title = DataUtil.readString(FileObject)
    x = DataUtil.readInt(FileObject)
    y = DataUtil.readInt(FileObject)
    z = DataUtil.readInt(FileObject)
    Direction = DataUtil.readInt(FileObject)
    return {'EntityID': EntityID,
            'Title': Title,
            'x': x,
            'y': y,
            'z': z,
            'Direction': Direction
    }


def handle1A(FileObject):
    EntityID = DataUtil.readInt(FileObject)
    x = DataUtil.readInt(FileObject)
    y = DataUtil.readInt(FileObject)
    z = DataUtil.readInt(FileObject)
    Count = DataUtil.readShort(FileObject)
    return {'EntityID': EntityID,
            'x': x,
            'y': y,
            'z': z,
            'Count': Count
    }


def handle1C(FileObject):
    EntityID = DataUtil.readInt(FileObject)
    VelocityX = DataUtil.readShort(FileObject)
    VelocityY = DataUtil.readShort(FileObject)
    VelocityZ = DataUtil.readShort(FileObject)
    return {'EntityID': EntityID,
            'VelocityX': VelocityX,
            'VelocityY': VelocityY,
            'VelocityZ': VelocityZ
    }


def handle1D(FileObject):
    EntityArrayLength = DataUtil.readByte(FileObject)
    Entities = []
    for i in range(EntityArrayLength):
        Entities.append(DataUtil.readInt(FileObject))
    return Entities


def handle1E(FileObject):
    EntityID = DataUtil.readInt(FileObject)
    return EntityID


def handle1F(FileObject):
    EntityID = DataUtil.readInt(FileObject)
    x = DataUtil.readByte(FileObject)
    y = DataUtil.readByte(FileObject)
    z = DataUtil.readByte(FileObject)
    return {'EntityID': EntityID,
            'x': x,
            'y': y,
            'z': z
    }


def handle20(FileObject):
    EntityID = DataUtil.readInt(FileObject)
    Yaw = DataUtil.readByte(FileObject)
    Pitch = DataUtil.readByte(FileObject)
    return {'EntityID': EntityID,
            'Yaw': Yaw,
            'Pitch': Pitch
    }


def handle21(FileObject):
    EntityID = DataUtil.readInt(FileObject)
    x = DataUtil.readByte(FileObject)
    y = DataUtil.readByte(FileObject)
    z = DataUtil.readByte(FileObject)
    Yaw = DataUtil.readByte(FileObject)
    Pitch = DataUtil.readByte(FileObject)
    return {'EntityID': EntityID,
            'x': x,
            'y': y,
            'z': z,
            'Yaw': Yaw,
            'Pitch': Pitch
    }


def handle22(FileObject):
    EntityID = DataUtil.readInt(FileObject)
    x = DataUtil.readInt(FileObject)
    y = DataUtil.readInt(FileObject)
    z = DataUtil.readInt(FileObject)
    Yaw = DataUtil.readByte(FileObject)
    Pitch = DataUtil.readByte(FileObject)
    return {'EntityID': EntityID,
            'x': x,
            'y': y,
            'z': z,
            'Yaw': Yaw,
            'Pitch': Pitch
    }


def handle23(FileObject):
    EntityID = DataUtil.readInt(FileObject)
    HeadYaw = DataUtil.readByte(FileObject)
    return {'EntityID': EntityID,
            'HeadYaw': HeadYaw
    }


def handle26(FileObject):
    EntityID = DataUtil.readInt(FileObject)
    Status = DataUtil.readByte(FileObject)
    return {'EntityID': EntityID,
            'Status': Status
    }


def handle27(FileObject):
    EntityID = DataUtil.readInt(FileObject)
    VehicleID = DataUtil.readInt(FileObject)
    return {'EntityID': EntityID,
            'VehicleID': VehicleID
    }


def handle28(FileObject):
    EntityID = DataUtil.readInt(FileObject)
    metadata = DataUtil.readEntityMetadata(FileObject)
    return {'EntityID': EntityID,
            'MetaData': metadata
    }


def handle29(FileObject):
    EntityID = DataUtil.readInt(FileObject)
    EffectID = DataUtil.readByte(FileObject)
    Amplifier = DataUtil.readByte(FileObject)
    Duration = DataUtil.readShort(FileObject)
    return {'EntityID': EntityID,
            'EffectID': EffectID,
            'Amplifier': Amplifier,
            'Duration': Duration
    }


def handle2A(FileObject):
    EntityID = DataUtil.readInt(FileObject)
    EffectID = DataUtil.readByte(FileObject)
    return {'EntityID': EntityID,
            'EffectID': EffectID
    }


def handle2B(FileObject):
    ExperienceBar = DataUtil.readFloat(FileObject)
    Level = DataUtil.readShort(FileObject)
    TotalExp = DataUtil.readShort(FileObject)
    return {'ExpBar': ExperienceBar,
            'Level': Level,
            'TotalExp': TotalExp
    }


def handle33(FileObject):
    X = DataUtil.readInt(FileObject)
    Z = DataUtil.readInt(FileObject)
    GroundUpContinuous = DataUtil.readBoolean(FileObject)
    PrimaryBitMap = DataUtil.readShort(FileObject)
    AddBitMap = DataUtil.readShort(FileObject)
    CompressedSize = DataUtil.readInt(FileObject)
    RawData = FileObject.read(CompressedSize)
    return {'x': X,
            'z': Z,
            'GroundUpContinuous': GroundUpContinuous,
            'PrimaryBitMap': PrimaryBitMap,
            'AddBitMap': AddBitMap,
            'RawData': RawData
    }


def handle34(FileObject):
    ChunkX = DataUtil.readInt(FileObject)
    ChunkZ = DataUtil.readInt(FileObject)
    AffectedBlocks = DataUtil.readShort(FileObject)
    DataSize = DataUtil.readInt(FileObject)
    FileObject.read(DataSize) #not going to be using this until I know how to.
    return {'ChunkX': ChunkX,
            'ChunkZ': ChunkZ,
            'AffectedBlocks': AffectedBlocks
    }


def handle35(FileObject):
    X = DataUtil.readInt(FileObject)
    Y = DataUtil.readByte(FileObject)
    Z = DataUtil.readInt(FileObject)
    BlockType = DataUtil.readShort(FileObject)
    BlockMetaData = DataUtil.readByte(FileObject)
    return {'x': X,
            'y': Y,
            'z': Z,
            'BlockType': BlockType,
            'MetaData': BlockMetaData
    }


def handle36(FileObject):
    X = DataUtil.readInt(FileObject)
    Y = DataUtil.readShort(FileObject)
    Z = DataUtil.readInt(FileObject)
    Byte1 = DataUtil.readByte(FileObject)
    Byte2 = DataUtil.readByte(FileObject)
    BlockID = DataUtil.readShort(FileObject)
    return {'x': X,
            'y': Y,
            'z': Z,
            'Byte1': Byte1,
            'Byte2': Byte2,
            'BlockID': BlockID
    }


def handle37(FileObject):
    #int - EntityID
    EntityID = DataUtil.readInt(FileObject)

    #int - X cord
    x = DataUtil.readInt(FileObject)

    #int - Y cord
    y = DataUtil.readInt(FileObject)

    #int - Z cord
    z = DataUtil.readInt(FileObject)

    #byte - Stage
    DestroyedStage = DataUtil.readByte(FileObject)
    return {'EntityID': EntityID,
            'x': x,
            'y': y,
            'z': z,
            'DestroyedStage': DestroyedStage
    }


def handle38(FileObject):
    #short - number of chunks
    ChunkCount = DataUtil.readShort(FileObject)

    #int - chunk data length
    ChunkDataLength = DataUtil.readInt(FileObject)
    SkyLightSent = DataUtil.readBoolean(FileObject)
    RawData = FileObject.read(ChunkDataLength)

    metadata = []
    for i in range(ChunkCount):
        ChunkX = DataUtil.readInt(FileObject)
        ChunkZ = DataUtil.readInt(FileObject)
        PrimaryBitMap = DataUtil.readUnsignedShort(FileObject)
        AddBitMap = DataUtil.readUnsignedShort(FileObject)
        metadata.append({'x': ChunkX,
                         'z': ChunkZ,
                         'PrimaryBitMap': PrimaryBitMap,
                         'AddBitMap': AddBitMap
                         })

    return {'ChunkCount': ChunkCount,
            'SkyLightSent': SkyLightSent,
            'RawData': RawData,
            'ChunkMeta': metadata
    }


def handle3C(FileObject):
    X = DataUtil.readDouble(FileObject)
    Y = DataUtil.readDouble(FileObject)
    Z = DataUtil.readDouble(FileObject)
    Radius = DataUtil.readFloat(FileObject)
    RecordCount = DataUtil.readInt(FileObject)
    AffectedBlocks = []
    for i in range((RecordCount * 3)):
        x = DataUtil.readByte(FileObject)
        y = DataUtil.readByte(FileObject)
        z = DataUtil.readByte(FileObject)
        AffectedBlocks.append({'x': x, 'y': y, 'z': z})
        #---Unknown what these floats do
    FileObject.read(4)
    FileObject.read(4)
    FileObject.read(4)
    #---
    return {'x': X,
            'y': Y,
            'z': Z,
            'Raidus': Radius,
            'AffectedBlocks': AffectedBlocks
    }


def handle3D(FileObject):
    EffectID = DataUtil.readInt(FileObject)
    X = DataUtil.readInt(FileObject)
    Y = DataUtil.readByte(FileObject)
    Z = DataUtil.readInt(FileObject)
    Data = DataUtil.readInt(FileObject)
    NoVolDecrease = DataUtil.readBoolean(FileObject)
    return {'EffectID': EffectID,
            'X': X,
            'Y': Y,
            'Z': Z,
            'Data': Data,
            'NoVolumeDecrease': NoVolDecrease
    }


def handle3E(FileObject):
    Sound = DataUtil.readString(FileObject)
    x = DataUtil.readInt(FileObject)
    y = DataUtil.readInt(FileObject)
    z = DataUtil.readInt(FileObject)
    Volume = DataUtil.readFloat(FileObject)
    Pitch = DataUtil.readByte(FileObject)
    return {'Sound': Sound,
            'x': x,
            'y': y,
            'z': z,
            'Volume': Volume,
            'Pitch': Pitch
    }
    
def handle3F(FileObject):
    name = DataUtil.readString(FileObject)
    x = DataUtil.readFloat(FileObject)
    y = DataUtil.readFloat(FileObject)
    z = DataUtil.readFloat(FileObject)
    offsetx = DataUtil.readFloat(FileObject)
    offsety = DataUtil.readFloat(FileObject)
    offsetz = DataUtil.readFloat(FileObject)
    speed = DataUtil.readFloat(FileObject)
    num = DataUtil.readInt(FileObject)
    return {'Name' : name,
            'x' : x,
            'y' : y,
            'z' : z,
            'Offset x' : offsetx,
            'Offset y' : offsety,
            'Offset z' : offsetz,
            'Speed' : speed,
            'Number' : num
    }


def handle46(FileObject):
    Reason = DataUtil.readByte(FileObject)
    GameMode = DataUtil.readByte(FileObject)
    return {'Reason': Reason,
            'GameMode': GameMode
    }


def handle47(FileObject):
    EntityID = DataUtil.readInt(FileObject)
    FileObject.read(1) #Boolean don't do nothing
    x = DataUtil.readInt(FileObject)
    y = DataUtil.readInt(FileObject)
    z = DataUtil.readInt(FileObject)
    return {'EntityID': EntityID,
            'x': x,
            'y': y,
            'z': z
    }


def handle64(FileObject):
    WindowID = DataUtil.readByte(FileObject)
    InventoryType = DataUtil.readByte(FileObject)
    WindowTitle = DataUtil.readString(FileObject)
    NumberOfSlots = DataUtil.readByte(FileObject)
    return {'WindowID': WindowID,
            'InventoryType': InventoryType,
            'WindowTitle': WindowTitle,
            'NumberOfSlots': NumberOfSlots
    }


def handle65(FileObject):
    WindowID = DataUtil.readByte(FileObject)
    return WindowID


def handle67(FileObject):
    WindowID = DataUtil.readByte(FileObject)
    Slot = DataUtil.readShort(FileObject)
    SlotData = DataUtil.readSlotData(FileObject)
    return {'WindowID': WindowID,
            'Slot': Slot,
            'SlotData': SlotData
    }


def handle68(FileObject):
    WindowID = DataUtil.readByte(FileObject)
    Count = DataUtil.readShort(FileObject)
    Slots = []
    for i in range(Count):
        SlotData = DataUtil.readSlotData(FileObject)
        Slots.append(SlotData)
    return {'WindowID': WindowID,
            'Count': Count,
            'Slots': Slots
    }


def handle69(FileObject):
    WindowID = DataUtil.readByte(FileObject)
    Property = DataUtil.readShort(FileObject)
    Value = DataUtil.readShort(FileObject)
    return {'WindowID': WindowID,
            'Property': Property,
            'Value': Value
    }


def handle6A(FileObject):
    WindowID = DataUtil.readByte(FileObject)
    ActionType = DataUtil.readShort(FileObject)
    Accepted = DataUtil.readBoolean(FileObject)
    return {'WindowID': WindowID,
            'ActionType': ActionType,
            'Accepted': Accepted
    }


def handle6B(FileObject):
    Slot = DataUtil.readShort(FileObject)
    ClickedItem = DataUtil.readSlotData(FileObject)
    return {'Slot': Slot,
            'ClickedItem': ClickedItem
    }


def handle82(FileObject):
    X = DataUtil.readInt(FileObject)
    Y = DataUtil.readShort(FileObject)
    Z = DataUtil.readInt(FileObject)
    Line1 = DataUtil.readString(FileObject)
    Line2 = DataUtil.readString(FileObject)
    Line3 = DataUtil.readString(FileObject)
    Line4 = DataUtil.readString(FileObject)
    return {'x': X,
            'y': Y,
            'z': Z,
            'Line1': Line1,
            'Line2': Line2,
            'Line3': Line3,
            'Line4': Line4
    }


def handle83(FileObject):
    ItemType = DataUtil.readShort(FileObject)
    ItemID = DataUtil.readShort(FileObject)
    TextLength = DataUtil.readShort(FileObject)
    Text = DataUtil.readByteArray(FileObject, TextLength)
    return {'ItemType': ItemType,
            'ItemID': ItemID,
            'Text': Text
    }


def handle84(FileObject):
    X = DataUtil.readInt(FileObject)
    Y = DataUtil.readShort(FileObject)
    Z = DataUtil.readInt(FileObject)
    Action = DataUtil.readByte(FileObject)
    DataLength = DataUtil.readShort(FileObject)
    if (DataLength != -1):
        ByteArray = DataUtil.readByteArray(FileObject, DataLength)
        NBTData = NBTFile(BytesIO(ByteArray), compression=NBTFile.Compression.GZIP)
        return {'x': X,
                'y': Y,
                'z': Z,
                'Action': Action,
                'NBTData': NBTData
        }
    return {'x': X,
            'y': Y,
            'z': Z,
            'Action': Action
    }


def handleC8(FileObject):
    StatID = DataUtil.readInt(FileObject)
    Amount = DataUtil.readByte(FileObject)
    return {'StatID': StatID,
            'Amount': Amount
    }


def handleC9(FileObject):
    PlayerName = DataUtil.readString(FileObject)
    Online = DataUtil.readBoolean(FileObject)
    Ping = DataUtil.readShort(FileObject)
    return {'PlayerName': PlayerName,
            'Online': Online,
            'Ping': Ping
    }


def handleCA(FileObject):
    #byte - flags
    Flags = DataUtil.readByte(FileObject)

    #byte - fly speed
    FlySpeed = DataUtil.readByte(FileObject)

    #byte - walk speed
    WalkSpeed = DataUtil.readByte(FileObject)
    return {'Flags': Flags,
            'Fly Speed': FlySpeed,
            'Walk Speed': WalkSpeed
    }

def handleCB(FileObject):
    text = DataUtil.readString(FileObject)
    return {'Text': text}
    
def handleCE(FileObject):
    name = DataUtil.readString(FileObject)
    display_text = DataUtil.readString(FileObject)
    create_or_remove = DataUtil.readBoolean(FileObject)
    return {'Name' : name,
            'Display Name' : display_text,
            'Remove' : create_or_remove
    }
    
def handleCF(FileObject):
    name = DataUtil.readString(FileObject)
    remove = DataUtil.readBoolean(FileObject)
    score_name = DataUtil.readString(FileObject)
    value = DataUtil.readInt(FileObject)
    return {'Item Name' : name,
            'Remove' : remove,
            'Score Name' : score_name,
            'Value' : value
    }

def handleD0(FileObject):
    position = DataUtil.readByte(FileObject)
    score = DataUtil.readString(FileObject)
    return {'Position' : position,
            'Score' : score
    }
    
def handleD1(FileObject):
    team = DataUtil.readString(FileObject)
    mode = DataUtil.readByte(FileObject)
    toReturn = {'Team' : team, 'Mode' : mode}
    if mode == 0 or mode == 2:
        toReturn['Display Name'] = DataUtil.readString(FileObject)
        toReturn['Prefix'] = DataUtil.readString(FileObject)
        toReturn['Suffix'] = DataUtil.readString(FileObject)
        toReturn['FriendlyFire'] = DataUtil.readByte(FileObject)
    if mode == 0 or mode == 3 or mode == 4:
        count = DataUtil.readShort(FileObject)
        players = []
        for i in range(count):
            players.append(DataUtil.readString(FileObject))
    return toReturn


def handleFA(FileObject):
    Channel = DataUtil.readString(FileObject)
    length = DataUtil.readShort(FileObject)
    message = DataUtil.readByteArray(FileObject, length)
    return {'Channel': Channel,
            'message': message
    }


def handleFC(FileObject):
    #short - shared secret length
    secretLength = DataUtil.readShort(FileObject)

    sharedSecret = DataUtil.readByteArray(FileObject, secretLength) #ignore this data, it doesn't matter

    #short - token length
    length = DataUtil.readShort(FileObject)

    token = DataUtil.readByteArray(FileObject, length) #ignore this data, it doesn't matter

    return {'Secret Length': secretLength,
            'Shared Secret': sharedSecret,
            'Token Length': length,
            'Token': token
    }


def handleFD(FileObject):
    #string - server id
    serverid = DataUtil.readString(FileObject)

    #short - pub key length
    length = DataUtil.readShort(FileObject)

    #byte array - pub key
    pubkey = DataUtil.readByteArray(FileObject, length)

    #short - token length
    length = DataUtil.readShort(FileObject)

    #byte array - token
    token = DataUtil.readByteArray(FileObject, length)

    return {'ServerID': serverid,
            'Public Key': pubkey,
            'Token': token
    }


def handleFF(FileObject):
    Reason = DataUtil.readString(FileObject)
    return {'Reason': Reason}

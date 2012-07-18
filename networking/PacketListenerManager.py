import struct
import sys
import zlib

def sendHandshake(FileObject, username, host, port):
    toSend = username + ";" + host + ":" + str(port)
    FileObject.send("\x02")
    FileObject.send(struct.pack('!h', toSend.__len__()))
    FileObject.send(toSend.encode('utf-16be'))

def sendLoginRequest(FileObject, username):
    FileObject.send("\x01")
    FileObject.send(struct.pack('!i', 29))
    FileObject.send(struct.pack('!h', username.__len__()))
    FileObject.send(username.encode('utf-16be','strict'))
    FileObject.send(struct.pack('!h', "hello".__len__()))
    FileObject.send("hello".encode('utf-16be','strict'))
    FileObject.send(struct.pack('!i', 0))
    FileObject.send(struct.pack('!i', 1))
    FileObject.send(struct.pack('!b', 0))
    FileObject.send(struct.pack('!B', 1))
    FileObject.send(struct.pack('!B', 0))

def handle00(FileObject, socket):
    KAid = struct.unpack('!i', FileObject.read(4))[0]
    socket.send("\x00" + struct.pack('!i', KAid))
    
def handle01(FileObject):
    Eid = struct.unpack('!i', FileObject.read(4))[0]
    length = struct.unpack('!h', FileObject.read(2))[0] * 2
    FileObject.read(length)
    length = struct.unpack('!h', FileObject.read(2))[0] * 2 
    world = FileObject.read(length).decode('utf-16be')
    mode = struct.unpack('!i', FileObject.read(4))[0]
    dimension = struct.unpack('!i', FileObject.read(4))[0]
    difficulty = struct.unpack('!b', FileObject.read(1))[0]
    FileObject.read(1)
    maxplayers = struct.unpack('!B', FileObject.read(1))[0]
    toReturn = {'EntityID' : Eid,
                'World' : world,
                'Mode' : mode,
                'Dimension' : dimension,
                'Difficulty' : difficulty,
                'MaxPlayers' : maxplayers
                }
    return toReturn

def handle02(FileObject):
    length = struct.unpack('!h', FileObject.read(2))[0] * 2
    message = FileObject.read(length)
    message = message.decode('utf-16be', 'strict')
    return message

def handle03(FileObject):
    length = struct.unpack('!h', FileObject.read(2))[0] * 2
    message = FileObject.read(length)
    message = message.decode('utf-16be','strict')
    return message

def handle04(FileObject):
    time = struct.unpack('!q', FileObject.read(8))[0]
    return time

def handle05(FileObject):
    EntityID = struct.unpack('!i', FileObject.read(4))[0]
    Slot = struct.unpack('!h', FileObject.read(2))[0]
    ItemID = struct.unpack('!h', FileObject.read(2))[0]
    Damage = struct.unpack('!h', FileObject.read(2))[0]
    return {'EntityID' : EntityID,
            'Slot' : Slot,
            'ItemID' : ItemID,
            'Damage' : Damage
            }

def handle06(FileObject):
    x = struct.unpack('!i', FileObject.read(4))[0]
    y = struct.unpack('!i', FileObject.read(4))[0]
    z = struct.unpack('!i', FileObject.read(4))[0]
    return {'x' : x,
            'y' : y,
            'z' : z
            }
    
def handle07(FileObject):
    userID = struct.unpack('!i', FileObject.read(4))[0]
    targetID = struct.unpack('!i', FileObject.read(4))[0]
    mButton = struct.unpack('?', FileObject.read(1))[0]
    return {'userID' : userID,
            'targetID' : targetID,
            'mButton' : mButton
            }
    
def handle08(FileObject):
    health = struct.unpack('!h', FileObject.read(2))[0]
    food = struct.unpack('!h', FileObject.read(2))[0]
    saturation = struct.unpack('!f', FileObject.read(4))[0]
    return {'health' : health,
            'food' : food,
            'saturation' : saturation
            }
    
def handle09(FileObject):
    dimension = struct.unpack('!i', FileObject.read(4))[0]
    difficulty = struct.unpack('!b', FileObject.read(1))[0]
    mode = struct.unpack('!b', FileObject.read(1))[0]
    height = struct.unpack('!h', FileObject.read(2))[0]
    length = struct.unpack('!h', FileObject.read(2))[0] * 2 
    world = FileObject.read(length).decode('utf-16be')
    return {'Dimension' : dimension,
            'Difficulty' : difficulty,
            'Mode' : mode,
            'Height' : height,
            'World' : world
            }
    
def handle0D(FileObject):
    x = struct.unpack('!d', FileObject.read(8))[0]
    stance = struct.unpack('!d', FileObject.read(8))[0]
    y = struct.unpack('!d', FileObject.read(8))[0]
    z = struct.unpack('!d', FileObject.read(8))[0]
    yaw = struct.unpack('!f', FileObject.read(4))[0]
    pitch = struct.unpack('!f', FileObject.read(4))[0]
    onGround = struct.unpack('?', FileObject.read(1))[0]
    return {'x' : x,
            'stance' : stance,
            'y' : y,
            'z' : z,
            'yaw' : yaw,
            'pitch' : pitch,
            'onGround' : onGround
            }
    
def handle11(FileObject):
    EntityID = struct.unpack('!i', FileObject.read(4))[0]
    FileObject.read(1) #Unused
    x = struct.unpack('!i', FileObject.read(4))[0]
    y = struct.unpack('!b', FileObject.read(1))[0]
    z = struct.unpack('!i', FileObject.read(4))[0]
    return {'EntityID' : EntityID,
            'x' : x,
            'y' : y,
            'z' : z
            }
    
def handle12(FileObject):
    EntityID = struct.unpack('!i', FileObject.read(4))[0]
    Animation = struct.unpack('!b', FileObject.read(1))[0]
    return {'EntityID' : EntityID,
            'AnimationID' : Animation
            }
    
def handle14(FileObject):
    EntityID = struct.unpack('!i', FileObject.read(4))[0]
    length = struct.unpack('!h', FileObject.read(2))[0] * 2
    PlayerName = FileObject.read(length).decode('utf-16be')
    x = struct.unpack('!i', FileObject.read(4))[0]
    y = struct.unpack('!i', FileObject.read(4))[0]
    z = struct.unpack('!i', FileObject.read(4))[0]
    yaw = struct.unpack('!f', FileObject.read(4))[0]
    pitch = struct.unpack('!f', FileObject.read(4))[0]
    curItem = struct.unpack('!h', FileObject.read(2))[0]
    toReturn = {'EntityID' : EntityID,
                'Player Name' : PlayerName,
                'x' : x,
                'y' : y,
                'z' : z,
                'yaw' : yaw,
                'pitch' : pitch,
                'curItem' : curItem
                }
    print toReturn
    return toReturn

def handle15(FileObject):
    EntityID = struct.unpack('!i', FileObject.read(4))[0]
    Item = struct.unpack('!h', FileObject.read(2))[0]
    Count = struct.unpack('!b', FileObject.read(1))[0]
    Damage = struct.unpack('!h', FileObject.read(2))[0]
    x = struct.unpack('!i', FileObject.read(4))[0]
    y = struct.unpack('!i', FileObject.read(4))[0]
    z = struct.unpack('!i', FileObject.read(4))[0]
    Rotation = struct.unpack('!b', FileObject.read(1))[0]
    Pitch = struct.unpack('!b', FileObject.read(1))[0]
    Roll = struct.unpack('!b', FileObject.read(1))[0]
    return {'EntityID' : EntityID,
            'Item' : Item,
            'Count' : Count,
            'Damage' : Damage,
            'x' : x,
            'y' : y,
            'z' : z,
            'Rotation' : Rotation,
            'Pitch' : Pitch,
            'Roll' : Roll
            }
    
def handle16(FileObject):
    CollectedID = struct.unpack('!i', FileObject.read(4))[0]
    CollectorID = struct.unpack('!i', FileObject.read(4))[0]
    return {'CollectedID' : CollectedID,
            'CollectorID' : CollectorID
            }
    
def handle17(FileObject):
    EntityID = struct.unpack('!i', FileObject.read(4))[0]
    Type = struct.unpack('!b', FileObject.read(1))[0]
    x = struct.unpack('!i', FileObject.read(4))[0]
    y = struct.unpack('!i', FileObject.read(4))[0]
    z = struct.unpack('!i', FileObject.read(4))[0]
    ThrowerEntityID = struct.unpack('!i', FileObject.read(4))[0]
    if(ThrowerEntityID > 0):
        SpeedX = struct.unpack('!h', FileObject.read(2))[0]
        SpeedY = struct.unpack('!h', FileObject.read(2))[0]
        SpeedZ = struct.unpack('!h', FileObject.read(2))[0]
        return {'EntityID' : EntityID,
                'Type' : Type,
                'x' : x,
                'y' : y,
                'z' : z,
                'ThrowerEntityID' : ThrowerEntityID,
                'SpeedX' : SpeedX,
                'SpeedY' : SpeedY,
                'SpeedZ' : SpeedZ
                }
    else:
        return {'EntityID' : EntityID,
                'Type' : Type,
                'x' : x,
                'y' : y,
                'z' : z,
                }
        
def handle18(FileObject):
    EntityID = struct.unpack('!i', FileObject.read(4))[0]
    Type = struct.unpack('!b', FileObject.read(1))[0]
    x = struct.unpack('!i', FileObject.read(4))[0]
    y = struct.unpack('!i', FileObject.read(4))[0]
    z = struct.unpack('!i', FileObject.read(4))[0]
    Yaw = struct.unpack('!b', FileObject.read(1))[0]
    Pitch = struct.unpack('!b', FileObject.read(1))[0]
    HeadYaw = struct.unpack('!b', FileObject.read(1))[0]
    metadata = {}
    x = struct.unpack('!b', FileObject.read(1))[0]
    while x != 127:
        index = x & 0x1F # Lower 5 bits
        ty    = x >> 5   # Upper 3 bits
        if ty == 0: val = struct.unpack('!b', FileObject.read(1))[0]
        if ty == 1: val = struct.unpack('!h', FileObject.read(2))[0]
        if ty == 2: val = struct.unpack('!i', FileObject.read(4))[0]
        if ty == 3: val = struct.unpack('!f', FileObject.read(4))[0] 
        if ty == 4: 
            length = struct.unpack('!h', FileObject.read(2))[0] * 2
            val = FileObject.read(length).decode('utf-16be')
        if ty == 5:
            val = {}
            val["id"]     = struct.unpack('!h', FileObject.read(2))[0]
            val["count"]  = struct.unpack('!b', FileObject.read(1))[0]
            val["damage"] = struct.unpack('!h', FileObject.read(2))[0]
        if ty == 6:
            val = []
            for i in range(3):
                val.append(struct.unpack('!i', FileObject.read(4))[0])
        metadata[index] = (ty, val)
        x = struct.unpack('!b', FileObject.read(1))[0]
    return {'EntityID' : EntityID,
            'Type' : Type,
            'x' : x,
            'y' : y,
            'z' : z,
            'Yaw' : Yaw,
            'Pitch' : Pitch,
            'HeadYaw' : HeadYaw,
            'Metadata' : metadata
            }
    
def handle19(FileObject):
    EntityID = struct.unpack('!i', FileObject.read(4))[0]
    length = struct.unpack('!h', FileObject.read(2))[0] * 2 
    Title = FileObject.read(length).decode('utf-16be')
    raw = FileObject.read(4)
    x = struct.unpack('!i', raw)[0]
    y = struct.unpack('!i', FileObject.read(4))[0]
    z = struct.unpack('!i', FileObject.read(4))[0]
    Direction = struct.unpack('!i', FileObject.read(4))[0]
    return {'EntityID' : EntityID,
            'Title' : Title,
            'x' : x,
            'y' : y,
            'z' : z,
            'Direction' : Direction
            }

def handle1A(FileObject):
    EntityID = struct.unpack('!i', FileObject.read(4))[0]
    x = struct.unpack('!i', FileObject.read(4))[0]
    y = struct.unpack('!i', FileObject.read(4))[0]
    z = struct.unpack('!i', FileObject.read(4))[0]
    Count = struct.unpack('!h', FileObject.read(2))[0]
    return {'EntityID' : EntityID,
            'x' : x,
            'y' : y,
            'z' : z,
            'Count' : Count
            }   
    
def handle1C(FileObject):
    EntityID = struct.unpack('!i', FileObject.read(4))[0]
    VelocityX = struct.unpack('!h', FileObject.read(2))[0]
    VelocityY = struct.unpack('!h', FileObject.read(2))[0]
    VelocityZ = struct.unpack('!h', FileObject.read(2))[0]
    return {'EntityID' : EntityID,
            'VelocityX' : VelocityX,
            'VelocityY' : VelocityY,
            'VelocityZ' : VelocityZ
            }
    
def handle1D(FileObject):
    EntityID = struct.unpack('!i', FileObject.read(4))[0]
    return EntityID

def handle1E(FileObject):
    EntityID = struct.unpack('!i', FileObject.read(4))[0]
    return EntityID

def handle1F(FileObject):
    EntityID = struct.unpack('!i', FileObject.read(4))[0]
    x = struct.unpack('!b', FileObject.read(1))[0]
    y = struct.unpack('!b', FileObject.read(1))[0]
    z = struct.unpack('!b', FileObject.read(1))[0]
    return {'EntityID' : EntityID,
            'x' : x,
            'y' : y,
            'z' : z
            }
    
def handle20(FileObject):
    EntityID = struct.unpack('!i', FileObject.read(4))[0]
    Yaw = struct.unpack('!b', FileObject.read(1))[0]
    Pitch = struct.unpack('!b', FileObject.read(1))[0]
    return {'EntityID' : EntityID,
            'Yaw' : Yaw,
            'Pitch' : Pitch
            }
    
def handle21(FileObject):
    EntityID = struct.unpack('!i', FileObject.read(4))[0]
    x = struct.unpack('!b', FileObject.read(1))[0]
    y = struct.unpack('!b', FileObject.read(1))[0]
    z = struct.unpack('!b', FileObject.read(1))[0]
    Yaw = struct.unpack('!b', FileObject.read(1))[0]
    Pitch = struct.unpack('!b', FileObject.read(1))[0]
    return {'EntityID' : EntityID,
            'x' : x,
            'y' : y,
            'z' : z,
            'Yaw' : Yaw,
            'Pitch' : Pitch
            }
    
def handle22(FileObject):
    EntityID = struct.unpack('!i', FileObject.read(4))[0]
    x = struct.unpack('!i', FileObject.read(4))[0]
    y = struct.unpack('!i', FileObject.read(4))[0]
    z = struct.unpack('!i', FileObject.read(4))[0]
    Yaw = struct.unpack('!b', FileObject.read(1))[0]
    Pitch = struct.unpack('!b', FileObject.read(1))[0]
    return {'EntityID' : EntityID,
            'x' : x,
            'y' : y,
            'z' : z,
            'Yaw' : Yaw,
            'Pitch' : Pitch
            }
    
def handle23(FileObject):
    EntityID = struct.unpack('!i', FileObject.read(4))[0]
    HeadYaw = struct.unpack('!b', FileObject.read(1))[0]
    return {'EntityID' : EntityID,
            'HeadYaw' : HeadYaw
            }
    
def handle26(FileObject):
    EntityID = struct.unpack('!i', FileObject.read(4))[0]
    Status = struct.unpack('!b', FileObject.read(1))[0]
    return {'EntityID' : EntityID,
            'Status' : Status
            }
    
def handle27(FileObject):
    EntityID = struct.unpack('!i', FileObject.read(4))[0]
    VehicleID = struct.unpack('!i', FileObject.read(4))[0]
    return {'EntityID' : EntityID,
            'VehicleID' : VehicleID
            }
    
def handle28(FileObject):
    EntityID = struct.unpack('!i', FileObject.read(4))[0]
    metadata = {}
    x = struct.unpack('!b', FileObject.read(1))[0]
    while x != 127:
        index = x & 0x1F # Lower 5 bits
        ty    = x >> 5   # Upper 3 bits
        if ty == 0: val = struct.unpack('!b', FileObject.read(1))[0]
        if ty == 1: val = struct.unpack('!h', FileObject.read(2))[0]
        if ty == 2: val = struct.unpack('!i', FileObject.read(4))[0]
        if ty == 3: val = struct.unpack('!f', FileObject.read(4))[0] 
        if ty == 4: 
            length = struct.unpack('!h', FileObject.read(2))[0] * 2
            val = FileObject.read(length).decode('utf-16be')
        if ty == 5:
            val = {}
            val["id"]     = struct.unpack('!h', FileObject.read(2))[0]
            val["count"]  = struct.unpack('!b', FileObject.read(1))[0]
            val["damage"] = struct.unpack('!h', FileObject.read(2))[0]
        if ty == 6:
            val = []
            for i in range(3):
                val.append(struct.unpack('!i', FileObject.read(4))[0])
        metadata[index] = (ty, val)
        x = struct.unpack('!b', FileObject.read(1))[0]
    return {'EntityID' : EntityID,
            'MetaData' : metadata
            }
    
def handle29(FileObject):
    EntityID = struct.unpack('!i', FileObject.read(4))[0]
    EffectID = struct.unpack('!b', FileObject.read(1))[0]
    Amplifier = struct.unpack('!b', FileObject.read(1))[0]
    Duration = struct.unpack('!h', FileObject.read(2))[0]
    return {'EntityID' : EntityID,
            'EffectID' : EffectID,
            'Amplifier' : Amplifier,
            'Duration' : Duration
            }
    
def handle2A(FileObject):
    EntityID = struct.unpack('!i', FileObject.read(4))[0]
    EffectID = struct.unpack('!b', FileObject.read(1))[0]
    return {'EntityID' : EntityID,
            'EffectID' : EffectID
            }
    
def handle2B(FileObject):
    ExperienceBar = struct.unpack('!f', FileObject.read(4))[0]
    Level = struct.unpack('!h', FileObject.read(2))[0]
    TotalExp = struct.unpack('!h', FileObject.read(2))[0]
    return {'ExpBar' : ExperienceBar,
            'Level' : Level,
            'TotalExp' : TotalExp
            }
    
def handle32(FileObject):
    X = struct.unpack('!i', FileObject.read(4))[0]
    raw = FileObject.read(4)
    Z = struct.unpack('!i', raw)[0]
    Mode = struct.unpack('?', FileObject.read(1))[0]
    return {'x' : X,
            'z' : Z,
            'Mode' : Mode
            }

def handle33(FileObject):
    X = struct.unpack('!i', FileObject.read(4))[0]
    Z = struct.unpack('!i', FileObject.read(4))[0]
    GroundUpContinous = struct.unpack('?', FileObject.read(1))[0]
    PrimaryBitMap = struct.unpack('!H', FileObject.read(2))[0]
    AddBitMap = struct.unpack('!H', FileObject.read(2))[0]
    CompressedSize = struct.unpack('!i', FileObject.read(4))[0]
    FileObject.read(4) #unused int
    FileObject.read(CompressedSize) #not going to be deflating and using this data until I know how to :3
    return {'x' : X,
            'z' : Z
            }
    
def handle34(FileObject):
    ChunkX = struct.unpack('!i', FileObject.read(4))[0]
    ChunkZ = struct.unpack('!i', FileObject.read(4))[0]
    AffectedBlocks = struct.unpack('!h', FileObject.read(2))[0]
    DataSize = struct.unpack('!i', FileObject.read(4))[0]
    FileObject.read(DataSize) #not going to be using this until I know how to.
    return {'ChunkX' : ChunkX,
            'ChunkZ' : ChunkZ,
            'AffectedBlocks' : AffectedBlocks
            }
    
def handle35(FileObject):
    X = struct.unpack('!i', FileObject.read(4))[0]
    Y = struct.unpack('!b', FileObject.read(1))[0]
    Z = struct.unpack('!i', FileObject.read(4))[0]
    BlockType = struct.unpack('!b', FileObject.read(1))[0]
    BlockMetaData = struct.unpack('!b', FileObject.read(1))[0]
    return {'x' : X,
            'y' : Y,
            'z' : Z,
            'BlockType' : BlockType,
            'MetaData' : BlockMetaData
            }
    
def handle36(FileObject):
    X = struct.unpack('!i', FileObject.read(4))[0]
    Y = struct.unpack('!h', FileObject.read(2))[0]
    Z = struct.unpack('!i', FileObject.read(4))[0]
    Byte1 = struct.unpack('!b', FileObject.read(1))[0]
    Byte2 = struct.unpack('!b', FileObject.read(1))[0]
    return {'x' : X,
            'y' : Y,
            'z' : Z,
            'Byte1' : Byte1,
            'Byte2' : Byte2
            }
    
def handle3C(FileObject):
    X = struct.unpack('!d', FileObject.read(8))[0]
    Y = struct.unpack('!d', FileObject.read(8))[0]
    Z = struct.unpack('!d', FileObject.read(8))[0]
    FileObject.read(4) #Unknown what this float does
    RecordCount = struct.unpack('!i', FileObject.read(4))[0]
    AffectedBlocks = []
    for i in range((RecordCount * 3)):
        x = struct.unpack('!b', FileObject.read(1))[0]
        y = struct.unpack('!b', FileObject.read(1))[0]
        z = struct.unpack('!b', FileObject.read(1))[0]
        AffectedBlocks.append({'x' : x, 'y' : y, 'z' : z})
    return {'X' : X,
            'Y' : Y,
            'Z' : Z,
            'AffectedBlocks' : AffectedBlocks
            }
    
def handle3D(FileObject):
    EffectID = struct.unpack('!i', FileObject.read(4))[0]
    X = struct.unpack('!i', FileObject.read(4))[0]
    Y = struct.unpack('!b', FileObject.read(1))[0]
    Z = struct.unpack('!i', FileObject.read(4))[0]
    Data = struct.unpack('!i', FileObject.read(4))[0]
    return {'EffectID' : EffectID,
            'X' : X,
            'Y' : Y,
            'Z' : Z,
            'Data' : Data
            }
    
def handle46(FileObject):
    Reason = struct.unpack('!b', FileObject.read(1))[0]
    GameMode = struct.unpack('!b', FileObject.read(1))[0]
    return {'Reason' : Reason,
            'GameMode' : GameMode
            }
    
def handle47(FileObject):
    EntityID = struct.unpack('!i', FileObject.read(4))[0]
    FileObject.read(1) #Boolean don't do nothing
    x = struct.unpack('!i', FileObject.read(4))[0]
    y = struct.unpack('!i', FileObject.read(4))[0]
    z = struct.unpack('!i', FileObject.read(4))[0]
    return {'EntityID' : EntityID,
            'x' : x,
            'y' : y,
            'z' : z
            }
    
def handle64(FileObject):
    WindowID = struct.unpack('!b', FileObject.read(1))[0]
    InventoryType = struct.unpack('!b', FileObject.read(1))[0]
    length = struct.unpack('!h', FileObject.read(2))[0] * 2
    WindowTitle = FileObject.read(length).decode("utf-16be")
    NumberOfSlots = struct.unpack('!b', FileObject.read(1))[0]
    return {'WindowID' : WindowID,
            'InventoryType' : InventoryType,
            'WindowTitle' : WindowTitle,
            'NumberOfSlots' : NumberOfSlots
            }
    
def handle65(FileObject):
    WindowID = struct.unpack('!b', FileObject.read(1))[0]
    return WindowID

def handle67(FileObject):
    WindowID = struct.unpack('!b', FileObject.read(1))[0]
    Slot = struct.unpack('!h', FileObject.read(2))[0]
    SlotData = decodeSlotData(FileObject)
    return {'WindowID' : WindowID,
            'Slot' : Slot,
            'SlotData' : SlotData
            }
    
def handle68(FileObject):
    WindowID = struct.unpack('!b', FileObject.read(1))[0]
    Count = struct.unpack('!h', FileObject.read(2))[0]
    Slots = []
    for i in range(Count):
        SlotData = decodeSlotData(FileObject)
        SlotData["index"] = i
        Slots.append(SlotData)
    return {'WindowID' : WindowID,
            'Count' : Count,
            'Slots' : Slots
            }
    
def handle69(FileObject):
    WindowID = struct.unpack('!b', FileObject.read(1))[0]
    Property = struct.unpack('!h', FileObject.read(2))[0]
    Value = struct.unpack('!h', FileObject.read(2))[0]
    return {'WindowID' : WindowID,
            'Property' : Property,
            'Value' : Value
            }
    
def handle6A(FileObject):
    WindowID = struct.unpack('!b', FileObject.read(1))[0]
    ActionType = struct.unpack('!h', FileObject.read(2))[0]
    Accepted = struct.unpack('?', FileObject.read(1))[0]
    return {'WindowID' : WindowID,
            'ActionType' : ActionType,
            'Accepted' : Accepted
            }
    
def handle6B(FileObject):
    Slot = struct.unpack('!h', FileObject.read(2))[0]
    ClickedItem = decodeSlotData(FileObject)
    return {'Slot' : Slot,
            'ClickedItem' : ClickedItem
            }
    
def handle82(FileObject):
    X = struct.unpack('!i', FileObject.read(4))[0]
    Y = struct.unpack('!h', FileObject.read(2))[0]
    Z = struct.unpack('!i', FileObject.read(4))[0]
    length = struct.unpack('!i', FileObject.read(2))[0] * 2
    Line1 = FileObject.read(length).decode("utf-16be")
    length = struct.unpack('!i', FileObject.read(2))[0] * 2
    Line2 = FileObject.read(length).decode("utf-16be")
    length = struct.unpack('!i', FileObject.read(2))[0] * 2
    Line3 = FileObject.read(length).decode("utf-16be")
    length = struct.unpack('!i', FileObject.read(2))[0] * 2
    Line4 = FileObject.read(length).decode("utf-16be")
    return {'x' : X,
            'y' : Y,
            'z' : Z,
            'Line1' : Line1,
            'Line2' : Line2,
            'Line3' : Line3,
            'Line4' : Line4
            }
    
def handle83(FileObject):
    ItemType = struct.unpack('!h', FileObject.read(2))[0]
    ItemID = struct.unpack('!h', FileObject.read(2))[0]
    TextLength = struct.unpack('!B', FileObject.read(1))[0]
    Text = struct.unpack(str(TextLength) + 'p', FileObject.read(TextLength))
    return {'ItemType' : ItemType,
            'ItemID' : ItemID,
            'Text' : Text
            }
    
def handle84(FileObject):
    X = struct.unpack('!i', FileObject.read(4))[0]
    Y = struct.unpack('!h', FileObject.read(2))[0]
    Z = struct.unpack('!i', FileObject.read(4))[0]
    Action = struct.unpack('!b', FileObject.read(1))[0]
    Custom1 = struct.unpack('!i', FileObject.read(4))[0]
    Custom2 = struct.unpack('!i', FileObject.read(4))[0]
    Custom3 = struct.unpack('!i', FileObject.read(4))[0]
    return {'x' : X,
            'y' : Y,
            'z' : Z,
            'Action' : Action,
            'Custom1' : Custom1,
            'Custom2' : Custom2,
            'Custom3': Custom3
            }
    
def handleC8(FileObject):
    StatID = struct.unpack('!i', FileObject.read(4))[0]
    Amount = struct.unpack('!b', FileObject.read(1))[0]
    return {'StatID' : StatID,
            'Amount' : Amount
            }    
    
def handleC9(FileObject):
    length = struct.unpack('!h', FileObject.read(2))[0] * 2
    PlayerName = FileObject.read(length).decode("utf-16be")
    Online = struct.unpack('?', FileObject.read(1))[0]
    Ping = struct.unpack('!h', FileObject.read(2))[0]
    return {'PlayerName' : PlayerName,
            'Online' : Online,
            'Ping' : Ping
            }
    
def handleCA(FileObject):
    Invulnerable = struct.unpack('?', FileObject.read(1))[0]
    IsFlying = struct.unpack('?', FileObject.read(1))[0]
    CanFly = struct.unpack('?', FileObject.read(1))[0]
    InstantDestroy = struct.unpack('?', FileObject.read(1))[0]
    return {'Invulnerable' : Invulnerable,
            'IsFlying' : IsFlying,
            'CanFly' : CanFly,
            'InstantDestroy' : InstantDestroy
            }
    
def handleFA(FileObject):
    length = struct.unpack('!h', FileObject.read(2))[0] * 2
    Channel = FileObject.read(length).decode("utf-16be")
    length = struct.unpack('!h', FileObject.read(2))[0]
    raw = FileObject.read(length)
    message = struct.unpack(str(length) + 's', raw)
    return {'Channel' : Channel,
            'message' : message
            }

def handleFF(FileObject):
    length = struct.unpack('!h', FileObject.read(2))[0] * 2
    Reason = FileObject.read(length)
    Reason = Reason.decode("utf-16be", 'strict')
    print Reason
    return Reason

def decodeSlotData(FileObject):
    Enchantables = ["\x103", "\x105", "\x15A", "\x167" , 
                    "\x10C", "\x10D", "\x10E", "\x10F", "\x122",
                    "\x110", "\x111", "\x112", "\x113", "\x123",
                    "\x10B", "\x100", "\x101", "\x102", "\x124",
                    "\x114", "\x115", "\x116", "\x117", "\x125",
                    "\x11B", "\x11C", "\x11D", "\x11E", "\x126"]
    BlockID = struct.unpack('!h', FileObject.read(2))[0]
    if(BlockID != -1):
        ItemCount = struct.unpack('!b', FileObject.read(1))[0]
        MetaData = struct.unpack('!h', FileObject.read(2))[0]
        if((256 <= BlockID and BlockID <= 259) or (267 <= BlockID and BlockID <= 279) or (283 <= BlockID and BlockID <= 286) or (290 <= BlockID and BlockID <= 294) or (298 <= BlockID and BlockID <= 317) or BlockID == 261 or BlockID == 359 or BlockID == 346):
            IncomingDataLength = struct.unpack('!h', FileObject.read(2))[0]
            if(IncomingDataLength != -1):
                raw = FileObject.read(IncomingDataLength)
                ByteArray = struct.unpack(str(IncomingDataLength) + "s", raw)[0]
                Data = zlib.decompress(ByteArray, 15+32)
                return {'BlockID' : BlockID,
                        'ItemCount' : ItemCount,
                        'MetaData' : MetaData,
                        'Data' : Data
                        }
        return {'BlockID' : BlockID,
                'ItemCount' : ItemCount,
                'MetaData' : MetaData
                }
    return {'BlockID' : -1,
            'ItemCount' : -1
            }

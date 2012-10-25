import struct
import zlib

def handle00(FileObject, socket):
    KAid = struct.unpack('!i', FileObject.read(4))[0]
    socket.send("\x00" + struct.pack('!i', KAid))
    
def handle01(FileObject):
    Eid = struct.unpack('!i', FileObject.read(4))[0]
    length = struct.unpack('!h', FileObject.read(2))[0] * 2 
    world = FileObject.read(length).decode('utf-16be')
    mode = struct.unpack('!b', FileObject.read(1))[0]
    dimension = struct.unpack('!b', FileObject.read(1))[0]
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
    dayTime = struct.unpack('!q', FileObject.read(8))[0]
    return {'Time' : time,
            'DayTime' : dayTime
            }

def handle05(FileObject):
    EntityID = struct.unpack('!i', FileObject.read(4))[0]
    Slot = struct.unpack('!h', FileObject.read(2))[0]
    Item = decodeSlotData(FileObject)
    return {'EntityID' : EntityID,
            'Slot' : Slot,
            'Item' : Item
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
    metadata = readEntityMetadata(FileObject)
    toReturn = {'EntityID' : EntityID,
                'Player Name' : PlayerName,
                'x' : x,
                'y' : y,
                'z' : z,
                'yaw' : yaw,
                'pitch' : pitch,
                'curItem' : curItem,
                'Metadata' : metadata
                }
    return toReturn

def handle15(FileObject):
    EntityID = struct.unpack('!i', FileObject.read(4))[0]
    ItemID = struct.unpack('!h', FileObject.read(2))[0]
    if (ItemID != -1):
        Count = struct.unpack('!b', FileObject.read(1))[0]
        Damage = struct.unpack('!h', FileObject.read(2))[0]
        ArrayLength = struct.unpack('!h', FileObject.read(2))[0]
        if (ArrayLength != -1):
            Array = FileObject.read(ArrayLength) #TODO: find out what this does and do stuff accrodingly
    x = struct.unpack('!i', FileObject.read(4))[0]
    y = struct.unpack('!i', FileObject.read(4))[0]
    z = struct.unpack('!i', FileObject.read(4))[0]
    Rotation = struct.unpack('!b', FileObject.read(1))[0]
    Pitch = struct.unpack('!b', FileObject.read(1))[0]
    Roll = struct.unpack('!b', FileObject.read(1))[0]
    toReturn = {'EntityID' : EntityID,
                'ItemID' : ItemID,
                'x' : x,
                'y' : y,
                'z' : z,
                'Rotation' : Rotation,
                'Pitch' : Pitch,
                'Roll' : Roll
                }
    if (ItemID != -1):
        toReturn['Count'] = Count
        toReturn['Damage'] = Damage
    return toReturn
    
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
    VelocityX = struct.unpack('!h', FileObject.read(2))[0]
    VelocityY = struct.unpack('!h', FileObject.read(2))[0]
    VelocityZ = struct.unpack('!h', FileObject.read(2))[0]
    metadata = readEntityMetadata(FileObject)

    return {'EntityID' : EntityID,
            'Type' : Type,
            'x' : x,
            'y' : y,
            'z' : z,
            'Yaw' : Yaw,
            'Pitch' : Pitch,
            'HeadYaw' : HeadYaw,
            'Metadata' : metadata,
            'VelocityX' : VelocityX,
            'VelocityY' : VelocityY,
            'VelocityZ' : VelocityZ
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
    EntityArrayLength = struct.unpack('!b', FileObject.read(1))[0]
    Entities = []
    for i in range(EntityArrayLength):
        Entities.append(struct.unpack('!i', FileObject.read(4))[0])
    return Entities

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
    metadata = readEntityMetadata(FileObject)
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

def handle33(FileObject):
    X = struct.unpack('!i', FileObject.read(4))[0]
    Z = struct.unpack('!i', FileObject.read(4))[0]
    GroundUpContinous = struct.unpack('?', FileObject.read(1))[0]
    PrimaryBitMap = struct.unpack('!H', FileObject.read(2))[0]
    AddBitMap = struct.unpack('!H', FileObject.read(2))[0]
    CompressedSize = struct.unpack('!i', FileObject.read(4))[0]
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
    BlockType = struct.unpack('!h', FileObject.read(2))[0]
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
    BlockID = struct.unpack('!h', FileObject.read(2))[0]
    return {'x' : X,
            'y' : Y,
            'z' : Z,
            'Byte1' : Byte1,
            'Byte2' : Byte2,
            'BlockID' : BlockID
            }
    
def handle37(FileObject):
    #int - EntityID
    EntityID = struct.unpack('!i', FileObject.read(4))[0]
    
    #int - X cord
    x = struct.unpack('!i', FileObject.read(4))[0]
    
    #int - Y cord
    y = struct.unpack('!i', FileObject.read(4))[0]
    
    #int - Z cord
    z = struct.unpack('!i', FileObject.read(4))[0]
    
    #byte - Stage
    DestroyedStage = struct.unpack('!b', FileObject.read(1))[0]
    return {'EntityID' : EntityID,
            'x' : x,
            'y' : y,
            'z' : z,
            'DestroyedStage' : DestroyedStage
            }
    
def handle38(FileObject):
    #short - number of chunks
    ChunkCount = struct.unpack('!h', FileObject.read(2))[0]
    
    #int - chunk data length
    ChunkDataLength = struct.unpack('!i', FileObject.read(4))[0]
    FileObject.read(ChunkDataLength) #just gonna ignore this for now
    
    #metadata - ignoring this
    for i in range(ChunkCount):
        FileObject.read(12)
    
    return {'ChunkCount' : ChunkCount
            }
    
def handle3C(FileObject):
    X = struct.unpack('!d', FileObject.read(8))[0]
    Y = struct.unpack('!d', FileObject.read(8))[0]
    Z = struct.unpack('!d', FileObject.read(8))[0]
    Radius = struct.unpack('!f', FileObject.read(4))[0]
    RecordCount = struct.unpack('!i', FileObject.read(4))[0]
    AffectedBlocks = []
    for i in range((RecordCount * 3)):
        x = struct.unpack('!b', FileObject.read(1))[0]
        y = struct.unpack('!b', FileObject.read(1))[0]
        z = struct.unpack('!b', FileObject.read(1))[0]
        AffectedBlocks.append({'x' : x, 'y' : y, 'z' : z})
    #---Unknown what these floats do
    FileObject.read(4)
    FileObject.read(4)
    FileObject.read(4)
    #---
    return {'x' : X,
            'y' : Y,
            'z' : Z,
            'Raidus' : Radius,
            'AffectedBlocks' : AffectedBlocks
            }
    
def handle3D(FileObject):
    EffectID = struct.unpack('!i', FileObject.read(4))[0]
    X = struct.unpack('!i', FileObject.read(4))[0]
    Y = struct.unpack('!b', FileObject.read(1))[0]
    Z = struct.unpack('!i', FileObject.read(4))[0]
    Data = struct.unpack('!i', FileObject.read(4))[0]
    NoVolDecrease = struct.unpack('?', FileObject.read(1))[0]
    return {'EffectID' : EffectID,
            'X' : X,
            'Y' : Y,
            'Z' : Z,
            'Data' : Data,
            'NoVolumeDecrease' : NoVolDecrease
            }
    
def handle3E(FileObject):
    length = struct.unpack('!h', FileObject.read(2))[0] * 2 
    Sound = FileObject.read(length).decode('utf-16be')
    x = struct.unpack('!i', FileObject.read(4))[0]
    y = struct.unpack('!i', FileObject.read(4))[0]
    z = struct.unpack('!i', FileObject.read(4))[0]
    Volume = struct.unpack('!f', FileObject.read(4))[0]
    Pitch = struct.unpack('!b', FileObject.read(1))[0]
    return {'Sound' : Sound,
            'x' : x,
            'y' : y,
            'z' : z,
            'Volume' : Volume,
            'Pitch' : Pitch
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
    length = struct.unpack('!h', FileObject.read(2))[0] * 2
    Line1 = FileObject.read(length).decode("utf-16be")
    length = struct.unpack('!h', FileObject.read(2))[0] * 2
    Line2 = FileObject.read(length).decode("utf-16be")
    length = struct.unpack('!h', FileObject.read(2))[0] * 2
    Line3 = FileObject.read(length).decode("utf-16be")
    length = struct.unpack('!h', FileObject.read(2))[0] * 2
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
    DataLength = struct.unpack('!h', FileObject.read(2))[0]
    if (DataLength != -1):
        NBTData = struct.unpack(str(DataLength) + "s", FileObject.read(DataLength))[0]
        return {'x' : X,
                'y' : Y,
                'z' : Z,
                'Action' : Action,
                'NBTData' : NBTData
                }
    return {'x' : X,
            'y' : Y,
            'z' : Z,
            'Action' : Action
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
    #byte - flags
    Flags = struct.unpack('!b', FileObject.read(1))[0]

    #byte - fly speed
    FlySpeed = struct.unpack('!b', FileObject.read(1))[0]
    
    #byte - walk speed
    WalkSpeed = struct.unpack('!b', FileObject.read(1))[0]
    return {'Flags' : Flags,
            'Fly Speed' : FlySpeed,
            'Walk Speed' : WalkSpeed
            }
    
def handleCB(FileObject):
    length = struct.unpack('!h', FileObject.read(2))[0] * 2
    text = FileObject.read(length).decode("utf-16be")
    return {'Text' : text}
    
def handleFA(FileObject):
    length = struct.unpack('!h', FileObject.read(2))[0] * 2
    Channel = FileObject.read(length).decode("utf-16be")
    length = struct.unpack('!h', FileObject.read(2))[0]
    raw = FileObject.read(length)
    message = struct.unpack(str(length) + 's', raw)
    return {'Channel' : Channel,
            'message' : message
            }
    
def handleFC(FileObject):
    
    #short - shared secret length
    secretLength = struct.unpack('!h', FileObject.read(2))[0]
    
    sharedSecret = struct.unpack(str(secretLength) + "s", FileObject.read(secretLength))[0] #ignore this data, it doesn't matter
    
    #short - token length
    length = struct.unpack('!h', FileObject.read(2))[0]
    
    token = struct.unpack(str(length) + "s", FileObject.read(length))[0] #ignore this data, it doesn't matter
    
    return {'Secret Length' : secretLength,
            'Shared Secret' : sharedSecret,
            'Token Length' : length,
            'Token' : token
            }
    
    
def handleFD(FileObject):
    
    #string - server id
    length = struct.unpack('!h', FileObject.read(2))[0] * 2
    serverid = FileObject.read(length).decode("utf-16be")
    
    #short - pub key length
    length = struct.unpack('!h', FileObject.read(2))[0]
    
    #byte array - pub key
    pubkey = struct.unpack(str(length) + "s", FileObject.read(length))[0]
    
    #short - token length
    length = struct.unpack('!h', FileObject.read(2))[0]
    
    #byte array - token
    token = struct.unpack(str(length) + "s", FileObject.read(length))[0]
    
    return {'ServerID' : serverid,
            'Public Key' : pubkey,
            'Token' : token
            }
    
def handleFF(FileObject):
    length = struct.unpack('!h', FileObject.read(2))[0] * 2
    Reason = FileObject.read(length)
    Reason = Reason.decode("utf-16be", 'strict')
    print Reason
    return Reason

def readEntityMetadata(FileObject):
    metadata = {}
    byte = struct.unpack('!B', FileObject.read(1))[0]
    while byte != 127:
        index = byte & 0x1F # Lower 5 bits
        ty    = byte >> 5   # Upper 3 bits
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
            if (val["id"] != -1):
                val["count"]  = struct.unpack('!b', FileObject.read(1))[0]
                val["damage"] = struct.unpack('!h', FileObject.read(2))[0]
        if ty == 6:
            val = []
            for i in range(3):
                val.append(struct.unpack('!i', FileObject.read(4))[0])
        metadata[index] = (ty, val)
        byte = struct.unpack('!B', FileObject.read(1))[0]
    return metadata

def decodeSlotData(FileObject):
    BlockID = struct.unpack('!h', FileObject.read(2))[0]
    if(BlockID != -1):
        ItemCount = struct.unpack('!b', FileObject.read(1))[0]
        Damage = struct.unpack('!h', FileObject.read(2))[0]
        MetadataLength = struct.unpack('!h', FileObject.read(2))[0]
        if(MetadataLength != -1):
            raw = FileObject.read(MetadataLength)
            ByteArray = struct.unpack(str(MetadataLength) + "s", raw)[0]
            Data = zlib.decompress(ByteArray, 15+32)
            return {'BlockID' : BlockID,
                    'ItemCount' : ItemCount,
                    'Damage' : Damage,
                    'Data' : Data
                    }
        return {'BlockID' : BlockID,
                'ItemCount' : ItemCount,
                'Damage' : Damage
                }
    return {'BlockID' : -1,
            'ItemCount' : 0
            }

import socket
import struct
import sys

def sendHandshake(socket, username, host, port):
    toSend = username + ";" + host + ":" + str(port)
    socket.send("\x02")
    socket.send(struct.pack('!h', toSend.__len__()))
    socket.send(toSend.encode('utf-16be'))

def sendLoginRequest(socket, username):
    socket.send("\x01")
    socket.send(struct.pack('!i', 29))
    socket.send(struct.pack('!h', username.__len__()))
    socket.send(username.encode('utf-16be','strict'))
    socket.send(struct.pack('!h', "hello".__len__()))
    socket.send("hello".encode('utf-16be','strict'))
    socket.send(struct.pack('!i', 0))
    socket.send(struct.pack('!i', 1))
    socket.send(struct.pack('!b', 0))
    socket.send(struct.pack('!B', 1))
    socket.send(struct.pack('!B', 0))

def handle00(socket):
    KAid = struct.unpack('!i', socket.recv(4))[0]
    print "Sending keep alive response " + str(KAid)
    socket.send("\x00" + struct.pack('!i', KAid))
    
def handle01(socket):
    Eid = struct.unpack('!i', socket.recv(4))[0]
    length = struct.unpack('!h', socket.recv(2))[0] * 2
    socket.recv(length)
    length = struct.unpack('!h', socket.recv(2))[0] * 2 
    world = socket.recv(length).decode('utf-16be')
    mode = struct.unpack('!i', socket.recv(4))[0]
    dimension = struct.unpack('!i', socket.recv(4))[0]
    difficulty = struct.unpack('!b', socket.recv(1))[0]
    socket.recv(1)
    maxplayers = struct.unpack('!B', socket.recv(1))[0]
    toReturn = {'EntityID' : Eid,
                'World' : world,
                'Mode' : mode,
                'Dimension' : dimension,
                'Difficulty' : difficulty,
                'MaxPlayers' : maxplayers
                }
    print toReturn
    return toReturn

def handle02(socket):
    length = struct.unpack('!h', socket.recv(2))[0] * 2
    message = socket.recv(length)
    message = message.decode('utf-16be', 'strict')
    return message

def handle03(socket):
    length = struct.unpack('!h', socket.recv(2))[0] * 2
    message = socket.recv(length)
    message = message.decode('utf-16be','strict')
    print message
    return message

def handle04(socket):
    time = struct.unpack('!q', socket.recv(8))[0]
    return time

def handle05(socket):
    EntityID = struct.unpack('!i', socket.recv(4))[0]
    Slot = struct.unpack('!h', socket.recv(2))[0]
    ItemID = struct.unpack('!h', socket.recv(2))[0]
    Damage = struct.unpack('!h', socket.recv(2))[0]
    return {'EntityID' : EntityID,
            'Slot' : Slot,
            'ItemID' : ItemID,
            'Damage' : Damage
            }

def handle06(socket):
    x = struct.unpack('!i', socket.recv(4))[0]
    y = struct.unpack('!i', socket.recv(4))[0]
    z = struct.unpack('!i', socket.recv(4))[0]
    return {'x' : x,
            'y' : y,
            'z' : z
            }
    
def handle07(socket):
    userID = struct.unpack('!i', socket.recv(4))[0]
    targetID = struct.unpack('!i', socket.recv(4))[0]
    mButton = struct.unpack('?', socket.recv(1))[0]
    return {'userID' : userID,
            'targetID' : targetID,
            'mButton' : mButton
            }
    
def handle08(socket):
    health = struct.unpack('!h', socket.recv(2))[0]
    food = struct.unpack('!h', socket.recv(2))[0]
    saturation = struct.unpack('!f', socket.recv(4))[0]
    return {'health' : health,
            'food' : food,
            'saturation' : saturation
            }
    
def handle09(socket):
    dimension = struct.unpack('!i', socket.recv(4))[0]
    difficulty = struct.unpack('!b', socket.recv(1))[0]
    mode = struct.unpack('!b', socket.recv(1))[0]
    height = struct.unpack('!h', socket.recv(2))[0]
    length = struct.unpack('!h', socket.recv(2))[0] * 2 
    world = socket.recv(length).decode('utf-16be')
    return {'Dimension' : dimension,
            'Difficulty' : difficulty,
            'Mode' : mode,
            'Height' : height,
            'World' : world
            }
    
def handle0D(socket):
    x = struct.unpack('!d', socket.recv(8))[0]
    stance = struct.unpack('!d', socket.recv(8))[0]
    y = struct.unpack('!d', socket.recv(8))[0]
    z = struct.unpack('!d', socket.recv(8))[0]
    yaw = struct.unpack('!f', socket.recv(4))[0]
    pitch = struct.unpack('!f', socket.recv(4))[0]
    onGround = struct.unpack('?', socket.recv(1))[0]
    return {'x' : x,
            'stance' : stance,
            'y' : y,
            'z' : z,
            'yaw' : yaw,
            'pitch' : pitch,
            'onGround' : onGround
            }
    
def handle11(socket):
    EntityID = struct.unpack('!i', socket.recv(4))[0]
    socket.recv(1) #Unused
    x = struct.unpack('!i', socket.recv(4))[0]
    y = struct.unpack('!b', socket.recv(1))[0]
    z = struct.unpack('!i', socket.recv(4))[0]
    return {'EntityID' : EntityID,
            'x' : x,
            'y' : y,
            'z' : z
            }
    
def handle12(socket):
    EntityID = struct.unpack('!i', socket.recv(4))[0]
    Animation = struct.unpack('!b', socket.recv(1))[0]
    return {'EntityID' : EntityID,
            'AnimationID' : Animation
            }
    
def handle14(socket):
    EntityID = struct.unpack('!i', socket.recv(4))[0]
    length = struct.unpack('!h', socket.recv(2))[0] * 2
    PlayerName = socket.recv(length).decode('utf-16be')
    x = struct.unpack('!i', socket.recv(4))[0]
    y = struct.unpack('!i', socket.recv(4))[0]
    z = struct.unpack('!i', socket.recv(4))[0]
    yaw = struct.unpack('!f', socket.recv(4))[0]
    pitch = struct.unpack('!f', socket.recv(4))[0]
    curItem = struct.unpack('!h', socket.recv(2))[0]
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

def handle15(socket):
    EntityID = struct.unpack('!i', socket.recv(4))[0]
    Item = struct.unpack('!h', socket.recv(2))[0]
    Count = struct.unpack('!b', socket.recv(1))[0]
    Damage = struct.unpack('!h', socket.recv(2))[0]
    x = struct.unpack('!i', socket.recv(4))[0]
    y = struct.unpack('!i', socket.recv(4))[0]
    z = struct.unpack('!i', socket.recv(4))[0]
    Rotation = struct.unpack('!b', socket.recv(1))[0]
    Pitch = struct.unpack('!b', socket.recv(1))[0]
    Roll = struct.unpack('!b', socket.recv(1))[0]
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
    
def handle16(socket):
    CollectedID = struct.unpack('!i', socket.recv(4))[0]
    CollectorID = struct.unpack('!i', socket.recv(4))[0]
    return {'CollectedID' : CollectedID,
            'CollectorID' : CollectorID
            }
    
def handle17(socket):
    EntityID = struct.unpack('!i', socket.recv(4))[0]
    Type = struct.unpack('!b', socket.recv(1))[0]
    x = struct.unpack('!i', socket.recv(4))[0]
    y = struct.unpack('!i', socket.recv(4))[0]
    z = struct.unpack('!i', socket.recv(4))[0]
    ThrowerEntityID = struct.unpack('!i', socket.recv(4))[0]
    if(ThrowerEntityID > 0):
        SpeedX = struct.unpack('!h', socket.recv(2))[0]
        SpeedY = struct.unpack('!h', socket.recv(2))[0]
        SpeedZ = struct.unpack('!h', socket.recv(2))[0]
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
        
def handle18(socket):
    EntityID = struct.unpack('!i', socket.recv(4))[0]
    Type = struct.unpack('!b', socket.recv(1))[0]
    x = struct.unpack('!i', socket.recv(4))[0]
    y = struct.unpack('!i', socket.recv(4))[0]
    z = struct.unpack('!i', socket.recv(4))[0]
    Yaw = struct.unpack('!b', socket.recv(1))[0]
    Pitch = struct.unpack('!b', socket.recv(1))[0]
    HeadYaw = struct.unpack('!b', socket.recv(1))[0]
    metadata = {}
    x = struct.unpack('!b', socket.recv(1))[0]
    while x != 127:
        index = x & 0x1F # Lower 5 bits
        ty    = x >> 5   # Upper 3 bits
        if ty == 0: val = struct.unpack('!b', socket.recv(1))[0]
        if ty == 1: val = struct.unpack('!h', socket.recv(2))[0]
        if ty == 2: val = struct.unpack('!i', socket.recv(4))[0]
        if ty == 3: val = struct.unpack('!f', socket.recv(4))[0] 
        if ty == 4: 
            length = struct.unpack('!h', socket.recv(2))[0] * 2
            val = socket.recv(length).decode('utf-16be')
        if ty == 5:
            val = {}
            val["id"]     = struct.unpack('!h', socket.recv(2))[0]
            val["count"]  = struct.unpack('!b', socket.recv(1))[0]
            val["damage"] = struct.unpack('!h', socket.recv(2))[0]
            if ty == 6:
                val = []
                for i in range(3):
                    val.append(struct.unpack('!i', socket.recv(4))[0])
        metadata[index] = (ty, val)
        x = struct.unpack('!b', socket.recv(1))[0]
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
    
def handle19(socket):
    EntityID = struct.unpack('!i', socket.recv(4))[0]
    length = struct.unpack('!h', socket.recv(2))[0] * 2 
    Title = socket.recv(length).decode('utf-16be')
    x = struct.unpack('!i', socket.recv(4))[0]
    y = struct.unpack('!i', socket.recv(4))[0]
    z = struct.unpack('!i', socket.recv(4))[0]
    Direction = struct.unpack('!i', socket.recv(4))[0]
    return {'EntityID' : EntityID,
            'Title' : Title,
            'x' : x,
            'y' : y,
            'z' : z,
            'Direction' : Direction
            }

def handle1A(socket):
    EntityID = struct.unpack('!i', socket.recv(4))[0]
    x = struct.unpack('!i', socket.recv(4))[0]
    y = struct.unpack('!i', socket.recv(4))[0]
    z = struct.unpack('!i', socket.recv(4))[0]
    Count = struct.unpack('!h', socket.recv(2))[0]
    return {'EntityID' : EntityID,
            'x' : x,
            'y' : y,
            'z' : z,
            'Count' : Count
            }   
    
def handle1C(socket):
    EntityID = struct.unpack('!i', socket.recv(4))[0]
    VelocityX = struct.unpack('!h', socket.recv(2))[0]
    VelocityY = struct.unpack('!h', socket.recv(2))[0]
    VelocityZ = struct.unpack('!h', socket.recv(2))[0]
    return {'EntityID' : EntityID,
            'VelocityX' : VelocityX,
            'VelocityY' : VelocityY,
            'VelocityZ' : VelocityZ
            }
    
def handle1D(socket):
    EntityID = struct.unpack('!i', socket.recv(4))[0]
    return EntityID

def handle1E(socket):
    EntityID = struct.unpack('!i', socket.recv(4))[0]
    return EntityID

def handle1F(socket):
    EntityID = struct.unpack('!i', socket.recv(4))[0]
    x = struct.unpack('!b', socket.recv(1))[0]
    y = struct.unpack('!b', socket.recv(1))[0]
    z = struct.unpack('!b', socket.recv(1))[0]
    return {'EntityID' : EntityID,
            'x' : x,
            'y' : y,
            'z' : z
            }
    
def handle20(socket):
    EntityID = struct.unpack('!i', socket.recv(4))[0]
    Yaw = struct.unpack('!b', socket.recv(1))[0]
    Pitch = struct.unpack('!b', socket.recv(1))[0]
    return {'EntityID' : EntityID,
            'Yaw' : Yaw,
            'Pitch' : Pitch
            }
    
def handle21(socket):
    EntityID = struct.unpack('!i', socket.recv(4))[0]
    x = struct.unpack('!b', socket.recv(1))[0]
    y = struct.unpack('!b', socket.recv(1))[0]
    z = struct.unpack('!b', socket.recv(1))[0]
    Yaw = struct.unpack('!b', socket.recv(1))[0]
    Pitch = struct.unpack('!b', socket.recv(1))[0]
    return {'EntityID' : EntityID,
            'x' : x,
            'y' : y,
            'z' : z,
            'Yaw' : Yaw,
            'Pitch' : Pitch
            }
    
def handle22(socket):
    EntityID = struct.unpack('!i', socket.recv(4))[0]
    x = struct.unpack('!i', socket.recv(4))[0]
    y = struct.unpack('!i', socket.recv(4))[0]
    z = struct.unpack('!i', socket.recv(4))[0]
    Yaw = struct.unpack('!b', socket.recv(1))[0]
    Pitch = struct.unpack('!b', socket.recv(1))[0]
    return {'EntityID' : EntityID,
            'x' : x,
            'y' : y,
            'z' : z,
            'Yaw' : Yaw,
            'Pitch' : Pitch
            }
    
def handle23(socket):
    EntityID = struct.unpack('!i', socket.recv(4))[0]
    HeadYaw = struct.unpack('!b', socket.recv(1))[0]
    return {'EntityID' : EntityID,
            'HeadYaw' : HeadYaw
            }
    
def handle26(socket):
    EntityID = struct.unpack('!i', socket.recv(4))[0]
    Status = struct.unpack('!b', socket.recv(1))[0]
    return {'EntityID' : EntityID,
            'Status' : Status
            }
    
def handle27(socket):
    EntityID = struct.unpack('!i', socket.recv(4))[0]
    VehicleID = struct.unpack('!i', socket.recv(4))[0]
    return {'EntityID' : EntityID,
            'VehicleID' : VehicleID
            }
    
def handle28(socket):
    EntityID = struct.unpack('!i', socket.recv(4))[0]
    metadata = {}
    x = struct.unpack('!b', socket.recv(1))[0]
    while x != 127:
        index = x & 0x1F # Lower 5 bits
        ty    = x >> 5   # Upper 3 bits
        if ty == 0: val = struct.unpack('!b', socket.recv(1))[0]
        if ty == 1: val = struct.unpack('!h', socket.recv(2))[0]
        if ty == 2: val = struct.unpack('!i', socket.recv(4))[0]
        if ty == 3: val = struct.unpack('!f', socket.recv(4))[0] 
        if ty == 4: 
            length = struct.unpack('!h', socket.recv(2))[0] * 2
            val = socket.recv(length).decode('utf-16be')
        if ty == 5:
            val = {}
            val["id"]     = struct.unpack('!h', socket.recv(2))[0]
            val["count"]  = struct.unpack('!b', socket.recv(1))[0]
            val["damage"] = struct.unpack('!h', socket.recv(2))[0]
            if ty == 6:
                val = []
                for i in range(3):
                    val.append(struct.unpack('!i', socket.recv(4))[0])
        metadata[index] = (ty, val)
        struct.unpack('!b', socket.recv(1))[0]
    return {'EntityID' : EntityID,
            'MetaData' : metadata
            }
    
def handle29(socket):
    EntityID = struct.unpack('!i', socket.recv(4))[0]
    EffectID = struct.unpack('!b', socket.recv(1))[0]
    Amplifier = struct.unpack('!b', socket.recv(1))[0]
    Duration = struct.unpack('!h', socket.recv(2))[0]
    return {'EntityID' : EntityID,
            'EffectID' : EffectID,
            'Amplifier' : Amplifier,
            'Duration' : Duration
            }
    
def handle2A(socket):
    EntityID = struct.unpack('!i', socket.recv(4))[0]
    EffectID = struct.unpack('!b', socket.recv(1))[0]
    return {'EntityID' : EntityID,
            'EffectID' : EffectID
            }
    
def handle2B(socket):
    ExperienceBar = struct.unpack('!f', socket.recv(4))[0]
    Level = struct.unpack('!h', socket.recv(2))[0]
    TotalExp = struct.unpack('!h', socket.recv(2))[0]
    return {'ExpBar' : ExperienceBar,
            'Level' : Level,
            'TotalExp' : TotalExp
            }
    
def handle32(socket):
    X = struct.unpack('!i', socket.recv(4))[0]
    Z = struct.unpack('!i', socket.recv(4))[0]
    Mode = struct.unpack('?', socket.recv(1))[0]
    return {'x' : X,
            'z' : Z,
            'Mode' : Mode
            }
    
def handleCA(socket):
    Invulnerable = struct.unpack('?', socket.recv(1))[0]
    IsFlying = struct.unpack('?', socket.recv(1))[0]
    CanFly = struct.unpack('?', socket.recv(1))[0]
    InstantDestroy = struct.unpack('?', socket.recv(1))[0]
    return {'Invulnerable' : Invulnerable,
            'IsFlying' : IsFlying,
            'CanFly' : CanFly,
            'InstantDestroy' : InstantDestroy
            }
    
def handleFA(socket):
    length = struct.unpack('!h', socket.recv(2))[0] * 2
    Channel = socket.recv(length)
    length = struct.unpack('!h', socket.recv(2))[0]
    raw = socket.recv(length)
    print raw
    message = struct.unpack(str(length) + 's', raw)
    return {'Channel' : Channel,
            'message' : message
            }

def handleFF(socket):
    length = struct.unpack('!h', socket.recv(2))[0] * 2
    Reason = socket.recv(length)
    Reason = Reason.decode("utf-16be", 'strict')
    print Reason
    return Reason

    

    
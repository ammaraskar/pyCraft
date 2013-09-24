import DataUtil

def send00(socket, KAid):
    #packet id
    socket.send("\x00")

    #int - keep alive id
    DataUtil.sendInt(socket, KAid)


def sendHandshake(socket, username, host, port):
    #packet id
    socket.send("\x02")

    #byte - protocol version
    DataUtil.sendByte(socket, 78)

    #string - username
    DataUtil.sendString(socket, username)

    #string - server host
    DataUtil.sendString(socket, host)

    #int - server port
    DataUtil.sendInt(socket, port)


def send03(socket, message):
    #packet id
    socket.send("\x03")

    #-----string - message-----#
    DataUtil.sendString(socket, message)


def sendCD(socket, payload):
    #packet id
    socket.send("\xCD")

    #payload - byte
    DataUtil.sendByte(socket, payload)


def sendFC(socket, secret, token):
    #packet id
    socket.send("\xFC")

    #shared secret
    DataUtil.sendShort(socket, secret.__len__()) #length
    socket.send(secret)

    #token
    DataUtil.sendShort(socket, token.__len__())
    socket.send(token)


def sendFF(socket, reason):
    #string - disconnect reason
    DataUtil.sendString(socket, reason)


#====
def send0B(socket, x, y, z, stance, onGround):
    #packet id
    socket.send("\x0B")

    DataUtil.sendDouble(socket, x)
    DataUtil.sendDouble(socket, y)
    DataUtil.sendDouble(socket, stance)
    DataUtil.sendDouble(socket, z)
    DataUtil.sendBoolean(socket, onGround) 


def send0D(socket, x, y, z, stance, yaw, pitch, onGround):
    #packet id
    socket.send("\x0D")

    DataUtil.sendDouble(socket, x)
    DataUtil.sendDouble(socket, y)
    DataUtil.sendDouble(socket, stance)
    DataUtil.sendDouble(socket, z)
    DataUtil.sendFloat(socket, yaw)
    DataUtil.sendFloat(socket, pitch)
    DataUtil.sendBoolean(socket, onGround) 


def sendCA(socket, flags, flySpeed, walkSpeed):
    #packet id
    socket.send("\xCA")

    DataUtil.sendByte(socket, flags)
    DataUtil.sendFloat(socket, flySpeed)
    DataUtil.sendFloat(socket, walkSpeed) 

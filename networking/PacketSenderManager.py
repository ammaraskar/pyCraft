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
    DataUtil.sendByte(socket, 47)
    
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
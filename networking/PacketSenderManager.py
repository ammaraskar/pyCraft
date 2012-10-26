import socket
import struct

def send00(socket, KAid):
    #packet id
    socket.send("\x00")
    
    #int - keep alive id
    socket.send(struct.pack('!i', KAid))

def sendHandshake(socket, username, host, port):
    #packet id
    socket.send("\x02")
    
    #byte - protocol version
    socket.send(struct.pack('!b', 47))
    
    #string - username
    socket.send(struct.pack('!h', username.__len__()))
    socket.send(username.encode('utf-16be'))
    
    #string - server host
    socket.send(struct.pack('!h', host.__len__()))
    socket.send(host.encode('utf-16be'))
    
    #int - server port
    socket.send(struct.pack('!i', port))

def send03(socket, message):
    #packet id
    socket.send("\x03")
    
    #-----string - message-----#
    socket.send(struct.pack('!h', message.__len__())) #length
    socket.send(message.encode("utf-16be")) #message
    
def sendCD(socket, payload):
    #packet id
    socket.send("\xCD")
    
    #payload - byte
    socket.send(struct.pack('!b', payload))
    
def sendFC(socket, secret, token):
    #packet id
    socket.send("\xFC")
    
    #shared secret
    socket.send(struct.pack('!h', secret.__len__())) #length
    socket.send(secret)
    
    #token
    socket.send(struct.pack('!h', token.__len__())) #length
    socket.send(token)
    
def sendFF(socket, reason):
    socket.send(struct.pack('!h', reason.__len__())) #length
    socket.send(reason.encode("utf-16be")) #message
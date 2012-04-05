import socket
import struct
import sys

def sendString( packetid, string, socket):
    length = struct.pack('!h', string.__len__())
    socket.send(packetid)
    socket.send(length)
    socket.send(string.encode('utf-16be','strict')) 
    
def readStringFromSocket(socket):
    response = socket.recv(256)
    packetid = response[0]
    response = response[3:]
    response = response.decode("utf-16be")
    return {'packetid' : packetid, 'string' : response}

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
    
def ReceiveLoginRequest(socket):
    response = socket.recv(256)
    packetid = response[0]
    if(packetid != "\x01"):
        return ""
    response = response[1:]
    
def handle00(socket, message):
    message = message[1:]
    message = struct.unpack('!i')
    socket.send("\x00")
    socket.send(struct.pack('!i'), message)

def handleFF(socket, message):
    message = message[3:]
    message = message.decode("utf-16be")
    print "Disconnected: " + message
    sys.exit()
    
def handleIncomingPacket(socket):
    response = socket.recv(256)
    if not response: 
        handleIncomingPacket(socket)
    packetid = response[0]
    print str(ord(packetid))
    if(packetid == "\x00"):
        handle00(socket, response)
    elif(packetid == "\xFF"):
        handleFF(socket, response)
    

    
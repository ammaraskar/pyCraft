import socket
import struct
import sys

def sendString( packetid, string, socket):
    length = struct.pack('!h', string.__len__())
    socket.send(packetid)
    socket.send(length)
    socket.send(string.encode('utf-16be','strict')) 

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
    socket.recv(length)
    mode = struct.unpack('!i', socket.recv(4))[0]
    dimension = struct.unpack('!i', socket.recv(4))[0]
    difficulty = struct.unpack('!b', socket.recv(1))[0]
    socket.recv(1)
    maxplayers = struct.unpack('!B', socket.recv(1))[0]
    toReturn = {'EntityID' : Eid,
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
    length = struct.unpack('!h', socket.recv(2))[0]
    message = socket.recv(length)
    message = message.decode('utf-16be','strict')
    print message
    return message

def handleFF(socket, response):
    response = socket.recv(2)
    length = struct.unpack('!h', response)[0] * 2
    response = socket.recv(length)
    response = response.decode("utf-16be", 'strict')
    print response
    return response

    

    
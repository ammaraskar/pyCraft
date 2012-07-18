import socket
import struct

def send03(socket, message):
    socket.send("\x03")
    socket.send(struct.pack('!h', message.__len__()))
    socket.send(message.encode("utf-16be"))
import socket
import wx
import PacketManager
import urllib2
import traceback
import threading
import struct

#Eclipse pyDev error fix
wx=wx

class ServerConnection:
    
    def __init__(self, window, username, password, sessionID, server, port):
        self.username = username
        self.password = password
        self.sessionID = sessionID
        self.server = server
        self.port = port
        self.window = window
        
    def attemptConnection(self):
        self.socket = socket.socket ( socket.AF_INET, socket.SOCK_STREAM )
        try:
            self.socket.connect ( ( self.server, self.port ) )
            PacketManager.sendString("\x02", self.username + self.server + ":" + str(self.port), self.socket)
            response = PacketManager.readStringFromSocket(self.socket)
            serverid = response['string']
            if(serverid != '-'):
                url = "http://session.minecraft.net/game/joinserver.jsp?user=" + self.username + "&sessionId=" + self.sessionID + "&serverId=" + serverid
                response = urllib2.urlopen(url).read()
                if(response != "OK"):
                    self.window.connectStatus.SetLabel("Response from sessions.minecraft.net wasn't OK")
                    return False
                PacketManager.sendLoginRequest(self.socket, self.username)
                PacketListener(self.window, self.socket).start()
        except Exception, e:
            self.window.connectStatus.SetForegroundColour(wx.RED)
            self.window.connectStatus.SetLabel("Connection to server failed")
            traceback.print_exc()
            return False
        
class PacketListener(threading.Thread):
    
    def __init__(self, window, socket):
        threading.Thread.__init__(self)
        self.socket = socket
        self.window = window
        
    def run(self):
        self.socket.settimeout(60)
        while True:
            try:
                response = self.socket.recv(256)
            except socket.timeout, e:
                self.window.connectStatus.SetLabel("Ping timeout")
                break
            print hex(ord(response[0]))
            if(response[0] == "\x00"):
                PacketManager.handle00(self.socket)
            if(response[0] == "\xFF"):
                response = response[3:].decode("utf-16be", 'strict')
                print response
                #DisconMessage = PacketManager.handleFF(self.socket, response)
                self.window.connectStatus.SetLabel("Disconnected: " + response)

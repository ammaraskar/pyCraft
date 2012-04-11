import socket
import wx
import PacketManager
import urllib2
import traceback
import threading
import struct

#Eclipse pyDev error fix
wx=wx

EntityID = 0

class ServerConnection(threading.Thread):
    
    def __init__(self, window, username, password, sessionID, server, port):
        threading.Thread.__init__(self)
        self.username = username
        self.password = password
        self.sessionID = sessionID
        self.server = server
        self.port = port
        if(window == None):
            self.NoGUI = True
        self.window = window
        
    def run(self):
        self.socket = socket.socket ( socket.AF_INET, socket.SOCK_STREAM )
        try:
            self.socket.connect ( ( self.server, self.port ) )
            PacketManager.sendString("\x02", self.username + ";" + self.server + ":" + str(self.port), self.socket)
            if(self.socket.recv(1) == "\x02"):
                response = PacketManager.handle02(self.socket)
            else:
                print "Server responded with a malformed packet"
                pass
            serverid = response
            if(serverid != '-'):
                url = "http://session.minecraft.net/game/joinserver.jsp?user=" + self.username + "&sessionId=" + self.sessionID + "&serverId=" + serverid
                response = urllib2.urlopen(url).read()
                if(response != "OK"):
                    if(self.NoGUI == False):
                        self.window.connectStatus.SetLabel("Response from sessions.minecraft.net wasn't OK")
                    else:
                        print "Response from sessions.minecraft.net wasn't OK, it was " + response
                    return False
                PacketManager.sendLoginRequest(self.socket, self.username)
                PacketListener(self.window, self.socket).start()
            else:
                print "Server is in offline mode"
                PacketManager.sendLoginRequest(self.socket, self.username)
        except Exception, e:
            if(self.NoGUI == False):
                self.window.connectStatus.SetForegroundColour(wx.RED)
                self.window.connectStatus.SetLabel("Connection to server failed")
            else:
                print "Connection to server failed"
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
                response = self.socket.recv(1)
            except socket.timeout, e:
                if(self.NoGUI == False):
                    self.window.connectStatus.SetLabel("Ping timeout")
                else:
                    print "Ping timeout"
                break
            print hex(ord(response[0]))
            if(response[0] == "\x00"):
                PacketManager.handle00(self.socket)
            if(response[0] == "\x01"):
                PacketManager.handle01(self.socket)
            if(response[0] == "\x03"):
                PacketManager.handle03(self.socket)
            if(response[0] == "\x04"):
                PacketManager.handle04(self.socket)
            if(response[0] == "\x05"):
                PacketManager.handle05(self.socket)
            if(response[0] == "\x06"):
                PacketManager.handle06(self.socket)
            if(response[0] == "\x07"):
                PacketManager.handle07(self.socket)
            if(response[0] == "\x08"):
                PacketManager.handle08(self.socket)
            if(response[0] == "\x09"):
                PacketManager.handle09(self.socket)
            if(response[0] == "\x0D"):
                PacketManager.handle0D(self.socket)
            if(response[0] == "\x11"):
                PacketManager.handle11(self.socket)
            if(response[0] == "\x12"):
                PacketManager.handle12(self.socket)
            if(response[0] == "\x14"):
                PacketManager.handle14(self.socket)
            if(response[0] == "\xFF"):
                DisconMessage = PacketManager.handleFF(self.socket, response)
                if(self.NoGUI == False):
                    "Disconnected: " + DisconMessage
                else:
                    self.window.connectStatus.SetLabel("Disconnected: " + DisconMessage)
    

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
            self.FileObject = self.socket.makefile()
            PacketManager.sendHandshake(self.socket, self.username, self.server, self.port)
            if(self.socket.recv(1) == "\x02"):
                response = PacketManager.handle02(self.FileObject)
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
                PacketListener(self.window, self.socket, self.FileObject).start()
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
    
    def __init__(self, window, socket, FileObject):
        threading.Thread.__init__(self)
        self.socket = socket
        self.window = window
        self.FileObject = FileObject
        
    def run(self):
        self.socket.setblocking(1)
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
                print PacketManager.handle00(self.FileObject, self.socket)
            if(response[0] == "\x01"):
                print PacketManager.handle01(self.FileObject)
            if(response[0] == "\x03"):
                print PacketManager.handle03(self.FileObject)
            if(response[0] == "\x04"):
                print PacketManager.handle04(self.FileObject)
            if(response[0] == "\x05"):
                print PacketManager.handle05(self.FileObject)
            if(response[0] == "\x06"):
                print PacketManager.handle06(self.FileObject)
            if(response[0] == "\x07"):
                print PacketManager.handle07(self.FileObject)
            if(response[0] == "\x08"):
                print PacketManager.handle08(self.FileObject)
            if(response[0] == "\x09"):
                print PacketManager.handle09(self.FileObject)
            if(response[0] == "\x0D"):
                print PacketManager.handle0D(self.FileObject)
            if(response[0] == "\x11"):
                print PacketManager.handle11(self.FileObject)
            if(response[0] == "\x12"):
                print PacketManager.handle12(self.FileObject)
            if(response[0] == "\x14"):
                print PacketManager.handle14(self.FileObject)
            if(response[0] == "\x15"):
                print PacketManager.handle15(self.FileObject)
            if(response[0] == "\x16"):
                print PacketManager.handle16(self.FileObject)
            if(response[0] == "\x17"):
                print PacketManager.handle17(self.FileObject)
            if(response[0] == "\x18"):
                print PacketManager.handle18(self.FileObject)
            if(response[0] == "\x19"):
                print PacketManager.handle19(self.FileObject)
            if(response[0] == "\x1A"):
                print PacketManager.handle1A(self.FileObject)
            if(response[0] == "\x1C"):
                print PacketManager.handle1C(self.FileObject)
            if(response[0] == "\x1D"):
                print PacketManager.handle1D(self.FileObject)
            if(response[0] == "\x1E"):
                print PacketManager.handle1E(self.FileObject)
            if(response[0] == "\x1F"):
                print PacketManager.handle1F(self.FileObject)
            if(response[0] == "\x20"):
                print PacketManager.handle20(self.FileObject)
            if(response[0] == "\x21"):
                print PacketManager.handle21(self.FileObject)
            if(response[0] == "\x22"):
                print PacketManager.handle22(self.FileObject)
            if(response[0] == "\x23"):
                print PacketManager.handle23(self.FileObject)
            if(response[0] == "\x26"):
                print PacketManager.handle26(self.FileObject)
            if(response[0] == "\x27"):
                print PacketManager.handle27(self.FileObject)
            if(response[0] == "\x28"):
                print PacketManager.handle28(self.FileObject)
            if(response[0] == "\x29"):
                print PacketManager.handle29(self.FileObject)
            if(response[0] == "\x2A"):
                print PacketManager.handle2A(self.FileObject)
            if(response[0] == "\x2B"): 
                print PacketManager.handle2B(self.FileObject)
            if(response[0] == "\x32"):
                print PacketManager.handle32(self.FileObject)
            if(response[0] == "\x33"):
                print PacketManager.handle33(self.FileObject)
            if(response[0] == "\x34"):
                print PacketManager.handle34(self.FileObject)
            if(response[0] == "\x35"):
                print PacketManager.handle35(self.FileObject)
            if(response[0] == "\x36"):
                print PacketManager.handle36(self.FileObject)
            if(response[0] == "\x3C"):
                print PacketManager.handle3C(self.FileObject)
            if(response[0] == "\x3D"):
                print PacketManager.handle3D(self.FileObject)
            if(response[0] == "\x46"):
                print PacketManager.handle46(self.FileObject)
            if(response[0] == "\x47"):
                print PacketManager.handle47(self.FileObject)
            if(response[0] == "\x64"):
                print PacketManager.handle64(self.FileObject)
            if(response[0] == "\x65"):
                print PacketManager.handle65(self.FileObject)
            if(response[0] == "\x67"):
                print PacketManager.handle67(self.FileObject)
            if(response[0] == "\x68"):
                print PacketManager.handle68(self.FileObject)
            if(response[0] == "\x69"):
                print PacketManager.handle69(self.FileObject)
            if(response[0] == "\x6A"):
                print PacketManager.handle6A(self.FileObject)
            if(response[0] == "\x6B"):
                print PacketManager.handle6B(self.FileObject)
            if(response[0] == "\x82"):
                print PacketManager.handle82(self.FileObject)
            if(response[0] == "\x83"):
                print PacketManager.handle83(self.FileObject)
            if(response[0] == "\x84"):
                print PacketManager.handle84(self.FileObject)
            if(response[0] == "\xC8"):
                print PacketManager.handleC8(self.FileObject)
            if(response[0] == "\xC9"):
                print PacketManager.handleC9(self.FileObject)
            if(response[0] == "\xCA"):
                print PacketManager.handleCA(self.FileObject)
            if(response[0] == "\xFA"):
                print PacketManager.handleFA(self.FileObject)
            if(response[0] == "\xFF"):
                DisconMessage = PacketManager.handleFF(self.FileObject)
                if(self.window == None):
                    print "Disconnected: " + DisconMessage
                else:
                    self.window.connectStatus.SetLabel("Disconnected: " + DisconMessage)
                break
    

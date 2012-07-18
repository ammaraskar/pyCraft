import socket
import wx
import PacketListenerManager
import urllib2
import traceback
import threading
import struct
from sys import stdout

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
        else:
            self.NoGUI = False
        self.window = window
        
    def setWindow(self, window):
        self.window = window
        
    def grabSocket(self):
        return self.socket 
                
    def run(self):
        self.socket = socket.socket ( socket.AF_INET, socket.SOCK_STREAM )
        try:
            self.socket.connect ( ( self.server, self.port ) )
            self.FileObject = self.socket.makefile()
            PacketListenerManager.sendHandshake(self.socket, self.username, self.server, self.port)
            if(self.socket.recv(1) == "\x02"):
                response = PacketListenerManager.handle02(self.FileObject)
            else:
                print "Server responded with a malformed packet"
                return False
            serverid = response
            if(serverid != '-'):
                try:
                    url = "http://session.minecraft.net/game/joinserver.jsp?user=" + self.username + "&sessionId=" + self.sessionID + "&serverId=" + serverid
                    response = urllib2.urlopen(url).read()
                    if(response != "OK"):
                        if(self.NoGUI == False):
                            self.window.ConnectPanel.Status.SetFont(wx.Font(15, wx.MODERN, wx.NORMAL, wx.NORMAL, 0, "Minecraft"))
                            self.window.ConnectPanel.Status.SetLabel("Response from sessions.minecraft.net wasn't OK")
                        else:
                            print "Response from sessions.minecraft.net wasn't OK, it was " + response
                            return False
                    PacketListenerManager.sendLoginRequest(self.socket, self.username)
                    if(self.NoGUI == False):
                        self.window.ConnectPanel.callbackAfterConnect()
                        while(not hasattr(self.window, 'text')):
                            continue
                    PacketListener(self, self.window, self.socket, self.FileObject).start()
                except Exception, e:
                    if(self.NoGUI == False and hasattr(self.window, 'ConnectPanel')):
                        self.window.ConnectPanel.Status.SetForegroundColour(wx.RED)
                        self.window.ConnectPanel.Status.SetLabel("Conection to sessions.mc.net failed")
                        self.window.ConnectPanel.RotationThread.Kill = True
            else:
                if(self.NoGUI):
                    print "Server is in offline mode"
                PacketListenerManager.sendLoginRequest(self.socket, self.username)
        except Exception, e:
            if(self.NoGUI == False and self.window):
                self.window.ConnectPanel.Status.SetForegroundColour(wx.RED)
                self.window.ConnectPanel.Status.SetLabel("Connection to server failed")
                self.window.ConnectPanel.RotationThread.Kill = True
            else:
                print "Connection to server failed"
            traceback.print_exc()
            return False
        #self.window.Status.SetLabel("Connected to " + self.server + "!")
                
class PacketListener(threading.Thread):
    
    def __init__(self, connection, window, socket, FileObject):
        threading.Thread.__init__(self)
        self.socket = socket
        self.window = window
        self.FileObject = FileObject
        self.connection = connection
        
    def run(self):
        self.socket.setblocking(1)
        while True:
            try:
                response = self.socket.recv(1)
            except Exception, e:
                if(self.window):
                    self.window.Status.SetLabel("Ping timeout")
                else:
                    print "Ping timeout"
                break
            #stdout.write((hex(ord(response[0]))) + ": ")
            if(response[0] == "\x00"):
                PacketListenerManager.handle00(self.FileObject, self.socket)
            if(response[0] == "\x01"):
                PacketListenerManager.handle01(self.FileObject)
            if(response[0] == "\x03"):
                message = PacketListenerManager.handle03(self.FileObject)
                if(self.connection.NoGUI):
                    print message.replace(u'\xa7', '&')
                elif(self.window):
                    self.window.handleChat(message)
            if(response[0] == "\x04"):
                PacketListenerManager.handle04(self.FileObject)
            if(response[0] == "\x05"):
                PacketListenerManager.handle05(self.FileObject)
            if(response[0] == "\x06"):
                PacketListenerManager.handle06(self.FileObject)
            if(response[0] == "\x07"):
                PacketListenerManager.handle07(self.FileObject)
            if(response[0] == "\x08"):
                PacketListenerManager.handle08(self.FileObject)
            if(response[0] == "\x09"):
                PacketListenerManager.handle09(self.FileObject)
            if(response[0] == "\x0D"):
                PacketListenerManager.handle0D(self.FileObject)
            if(response[0] == "\x11"):
                PacketListenerManager.handle11(self.FileObject)
            if(response[0] == "\x12"):
                PacketListenerManager.handle12(self.FileObject)
            if(response[0] == "\x14"):
                PacketListenerManager.handle14(self.FileObject)
            if(response[0] == "\x15"):
                PacketListenerManager.handle15(self.FileObject)
            if(response[0] == "\x16"):
                PacketListenerManager.handle16(self.FileObject)
            if(response[0] == "\x17"):
                PacketListenerManager.handle17(self.FileObject)
            if(response[0] == "\x18"):
                PacketListenerManager.handle18(self.FileObject)
            if(response[0] == "\x19"):
                PacketListenerManager.handle19(self.FileObject)
            if(response[0] == "\x1A"):
                PacketListenerManager.handle1A(self.FileObject)
            if(response[0] == "\x1C"):
                PacketListenerManager.handle1C(self.FileObject)
            if(response[0] == "\x1D"):
                PacketListenerManager.handle1D(self.FileObject)
            if(response[0] == "\x1E"):
                PacketListenerManager.handle1E(self.FileObject)
            if(response[0] == "\x1F"):
                PacketListenerManager.handle1F(self.FileObject)
            if(response[0] == "\x20"):
                PacketListenerManager.handle20(self.FileObject)
            if(response[0] == "\x21"):
                PacketListenerManager.handle21(self.FileObject)
            if(response[0] == "\x22"):
                PacketListenerManager.handle22(self.FileObject)
            if(response[0] == "\x23"):
                PacketListenerManager.handle23(self.FileObject)
            if(response[0] == "\x26"):
                PacketListenerManager.handle26(self.FileObject)
            if(response[0] == "\x27"):
                PacketListenerManager.handle27(self.FileObject)
            if(response[0] == "\x28"):
                PacketListenerManager.handle28(self.FileObject)
            if(response[0] == "\x29"):
                PacketListenerManager.handle29(self.FileObject)
            if(response[0] == "\x2A"):
                PacketListenerManager.handle2A(self.FileObject)
            if(response[0] == "\x2B"): 
                PacketListenerManager.handle2B(self.FileObject)
            if(response[0] == "\x32"):
                PacketListenerManager.handle32(self.FileObject)
            if(response[0] == "\x33"):
                PacketListenerManager.handle33(self.FileObject)
            if(response[0] == "\x34"):
                PacketListenerManager.handle34(self.FileObject)
            if(response[0] == "\x35"):
                PacketListenerManager.handle35(self.FileObject)
            if(response[0] == "\x36"):
                PacketListenerManager.handle36(self.FileObject)
            if(response[0] == "\x3C"):
                PacketListenerManager.handle3C(self.FileObject)
            if(response[0] == "\x3D"):
                PacketListenerManager.handle3D(self.FileObject)
            if(response[0] == "\x46"):
                PacketListenerManager.handle46(self.FileObject)
            if(response[0] == "\x47"):
                PacketListenerManager.handle47(self.FileObject)
            if(response[0] == "\x64"):
                PacketListenerManager.handle64(self.FileObject)
            if(response[0] == "\x65"):
                PacketListenerManager.handle65(self.FileObject)
            if(response[0] == "\x67"):
                PacketListenerManager.handle67(self.FileObject)
            if(response[0] == "\x68"):
                PacketListenerManager.handle68(self.FileObject)
            if(response[0] == "\x69"):
                PacketListenerManager.handle69(self.FileObject)
            if(response[0] == "\x6A"):
                PacketListenerManager.handle6A(self.FileObject)
            if(response[0] == "\x6B"):
                PacketListenerManager.handle6B(self.FileObject)
            if(response[0] == "\x82"):
                PacketListenerManager.handle82(self.FileObject)
            if(response[0] == "\x83"):
                PacketListenerManager.handle83(self.FileObject)
            if(response[0] == "\x84"):
                PacketListenerManager.handle84(self.FileObject)
            if(response[0] == "\xC8"):
                PacketListenerManager.handleC8(self.FileObject)
            if(response[0] == "\xC9"):
                PacketListenerManager.handleC9(self.FileObject)
            if(response[0] == "\xCA"):
                PacketListenerManager.handleCA(self.FileObject)
            if(response[0] == "\xFA"):
                PacketListenerManager.handleFA(self.FileObject)
            if(response[0] == "\xFF"):
                DisconMessage = PacketListenerManager.handleFF(self.FileObject)
                if(self.window == None):
                    print "Disconnected: " + DisconMessage
                elif(self.window):
                    if(hasattr(self.window, 'ChatPanel')):
                        self.window.ChatPanel.Status.SetLabel("Disconnected: " + DisconMessage)
                    elif(hasattr(self.window, 'Status')):
                        self.window.Status.SetLabel("Disconnected: " + DisconMessage)
                self.socket.close()
                break
    

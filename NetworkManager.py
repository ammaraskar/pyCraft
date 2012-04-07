import socket
import wx
import PacketManager
import urllib2
import traceback

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
        except Exception, e:
            self.window.connectStatus.SetForegroundColour(wx.RED)
            self.window.connectStatus.SetLabel("Connection to server failed")
            traceback.print_exc()
            return False
        
        
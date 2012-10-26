import urllib
import urllib2
import getpass
import sys
import NoGUIstuff
import time
import threading
from networking import PacketSenderManager, NetworkManager
from optparse import OptionParser
wxImportError = False
try:
    import wx
    import GUI
    wx = wx
except ImportError:
    print "wxPython not found, falling back to no gui version"
    wxImportError = True
      
class MinecraftLoginThread(threading.Thread):
    
    def __init__(self, window, rotationthread, username, password):
        threading.Thread.__init__(self)
        self.username = username
        self.password = password
        self.window = window
        self.rotationthread = rotationthread
               
    def run(self):
        url = 'https://login.minecraft.net'
        header = {'Content-Type' : 'application/x-www-form-urlencoded'}
        data = {'user' : self.username, 
                'password' : self.password,
                'version' : '13'}
        try:
            data = urllib.urlencode(data)
            req = urllib2.Request(url, data, header)
            opener = urllib2.build_opener()
            response = opener.open(req)
            response = response.read()
        except urllib2.URLError:
            self.rotationthread.Kill = True
            self.window.Status.SetForegroundColour(wx.RED)
            self.window.Status.SetLabel('Connection to minecraft.net failed')
            return
        if(response == "Bad login"):
            self.rotationthread.Kill = True
            self.window.Status.SetForegroundColour(wx.RED)
            self.window.Status.SetLabel('Incorrect username or password')
            return
        if(response == "Account migrated, use e-mail as username."):
            self.rotationthread.Kill = True
            self.window.Status.SetForegroundColour(wx.RED)
            self.window.Status.SetLabel('Account migrated, use e-mail as username.')
        response = response.split(":")
        username = response[2]
        sessionID = response[3]
        #KeepConnectionAlive(self.username, self.password, self.window).start()
        self.window.parent.username = username
        self.window.parent.sessionID = sessionID
        self.window.loggedIn = True
        self.window.handlePostLogin(self.rotationthread)
        
class KeepConnectionAlive(threading.Thread):
    
    def __init__(self, username, password, window):
        threading.Thread.__init__(self)
        self.username = username
        self.password = password
        self.window = window
     
    def run(self):
        while True:
            time.sleep(300)   
            url = 'https://login.minecraft.net'
            header = {'Content-Type' : 'application/x-www-form-urlencoded'}
            data = {'user' : self.username,
                    'password' : self.password,
                    'version' : '13'}
            try:
                data = urllib.urlencode(data)
                req = urllib2.Request(url, data, header)
                opener = urllib2.build_opener()
                response = opener.open(req)
                response = response.read()
            except urllib2.URLError:
                popup = wx.MessageBox('Keep alive to minecraft.net failed', 'Warning', 
                              wx.OK | wx.ICON_ERROR)
                popup.ShowModal()
            if(response == "Bad login"):
                popup = wx.MessageBox('Keep alive to minecraft.net failed (Incorrect username/password)', 'Warning', 
                              wx.OK | wx.ICON_ERROR)
                popup.ShowModal()
                return
            response = response.split(":")
            sessionID = response[3]
            if(self.window != None):
                self.window.parent.sessionID = sessionID
                self.window.parent.loggedIn = True            

if __name__ == "__main__":
        
    parser = OptionParser()
    
    parser.add_option("-n", "--nogui",
                  action="store_true", dest="noGUI", default=False,
                  help="don't use a GUI")
    
    parser.add_option("-u", "--username", dest="username", default="",
                  help="username to log in with (only with no gui mode)")
    
    parser.add_option("-p", "--password", dest="password", default="",
                  help="password to log in with (only with no gui mode)")
    
    parser.add_option("-s", "--server", dest="server", default="",
                  help="server to connect to (only with no gui mode)")
    
    parser.add_option("-d", "--dump-packets", 
                  action="store_true", dest="dumpPackets", default=False,
                  help="run with this argument to dump packets")
    
    parser.add_option("-o", "--out-file", dest="filename", default="dump.txt",
                  help="file to dump packets to")
    
    (options, args) = parser.parse_args()
            
    if(options.noGUI or wxImportError):
        if(options.username != ""):
            user = options.username
        else:
            user = raw_input("Enter your username: ")
        if(options.password != ""):
            passwd = options.password
        else:
            passwd = getpass.getpass("Enter your password: ")
        derp = NoGUIstuff.loginToMinecraft(user, passwd)
        if(derp['Response'] != "Good to go!"):
            print derp['Response']
            sys.exit()
        sessionid = derp['SessionID']
        print "Logged in as " + derp['Username'] + "! Your session id is: " + sessionid
        if(options.server != ""):
            stuff = options.server
        else:
            stuff = raw_input("Enter host and port if any: ")
        if ':' in stuff:
            StuffEnteredIntoBox = stuff.split(":")
            host = StuffEnteredIntoBox[0]
            port = int(StuffEnteredIntoBox[1])
        else:
            host = stuff
            port = 25565
        connection = NetworkManager.ServerConnection(None, derp['Username'], passwd, sessionid, host, port, options)
        connection.start()
        while True:
            try:
                chat_input = raw_input()
                if (connection.isConnected):
                    PacketSenderManager.send03(connection.grabSocket(), chat_input) 
                else:
                    pass       
            except KeyboardInterrupt, e:
                connection.disconnect()
                sys.exit(1)
    else:
        app = wx.PySimpleApp()
        Login = GUI.MainFrame(None, -1, "")
        app.SetTopWindow(Login)
        Login.Show()
        app.MainLoop()
        app2 = wx.PySimpleApp()
        ChatPanel = GUI.ServerChatPanel(None, -1, "pyCraft")
        app2.SetTopWindow(ChatPanel)
        ChatPanel.Show()
        app2.MainLoop()

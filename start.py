import urllib
import urllib2
import getpass
import sys
import PacketSenderManager
import NetworkManager
import NoGUIstuff
import time
import threading
import wx
import GUI

#pyDev error fix
wx=wx
        
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
        response = response.split(":")
        username = response[2]
        sessionID = response[3]
        KeepConnectionAlive(self.username, self.password).start()
        self.window.username = username
        self.window.sessionID = sessionID
        self.window.loggedIn = True
        self.window.handlePostLogin(self.rotationthread)
        
class KeepConnectionAlive(threading.Thread):
    
    def __init__(self, username, password):
        threading.Thread.__init__(self)
        self.username = username
        self.password = password
     
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
                opener.open(req)
            except urllib2.URLError:
                popup = wx.MessageBox('Keep alive to minecraft.net failed', 'Warning', 
                              wx.OK | wx.ICON_ERROR)
                popup.ShowModal()
        
if __name__ == "__main__":
    if (len(sys.argv) > 1):
        if(sys.argv[1] == "nogui"):
            user = raw_input("Enter your username: ")
            passwd = getpass.getpass("Enter your password: ")
            derp = NoGUIstuff.loginToMinecraft(user, passwd)
            if(derp['Response'] == "Incorrect username/password" or derp['Response'] == "Can't connect to minecraft.net"):
                print derp['Response']
                sys.exit()                
            sessionid = derp['SessionID']
            print "Logged in as " + derp['Username'] + "! Your session id is: " + sessionid
            stuff = raw_input("Enter host and port if any: ")
            if ':' in stuff:
                StuffEnteredIntoBox = stuff.split(":")
                host = StuffEnteredIntoBox[0]
                port = int(StuffEnteredIntoBox[1])
            else:
                host = stuff
                port = 25565
            connection = NetworkManager.ServerConnection(None, derp['Username'], passwd, sessionid, host, port)
            connection.start()
            raw_input()
            PacketSenderManager.send03(connection.grabSocket(), "/report Test report from pyCraft, hope this works :3")
    else:
        app = wx.PySimpleApp(0)
        Login = GUI.LoginFrame(None, -1, "")
        app.SetTopWindow(Login)
        Login.Show()
        app.MainLoop()

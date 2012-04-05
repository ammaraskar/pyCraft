import urllib
import urllib2
import getpass
import socket
import sys
import PacketManager
import Tkinter
import threading
from Tkinter import *

sessionid = ""
username = ""
        
class LoginWindow(Tkinter.Tk):
    def __init__(self,parent):
        Tkinter.Tk.__init__(self,parent)
        self.parent = parent
        self.initialize()

    def initialize(self):
        self.f = Frame(self)
        self.f.grid()
        
        #Variable defintions
        self.loginVariable = Tkinter.StringVar()
        self.loginVariable.set("Username: ")
        self.usernameEntry = Tkinter.StringVar()
        self.passwordLabel = Tkinter.StringVar()
        self.passwordLabel.set("Password: ")
        self.passwordEntry = Tkinter.StringVar()
        self.status = Tkinter.StringVar()
        self.LoggedIn = Tkinter.BooleanVar()
        self.LoggedIn.set(False)
        self.sessionID = Tkinter.StringVar()
        self.username = Tkinter.StringVar()
        #Username label#
        self.Usernamelabel = Tkinter.Label(self.f,textvariable=self.loginVariable,
                              anchor="w")
        self.Usernamelabel.grid(column=0,row=0,sticky='EW')
        #Username label#
        
        #Login text entry box
        self.UsernameEntry = Tkinter.Entry(self.f,textvariable=self.usernameEntry)
        self.UsernameEntry.grid(column=2,row=0,columnspan=2,sticky='EW')
        self.UsernameEntry.bind("<Return>", self.onPressEnterOnFields)
        #Login text entry box
        
        #Password label#
        self.Passwordlabel = Tkinter.Label(self.f,textvariable=self.passwordLabel,anchor="w")
        self.Passwordlabel.grid(column=0,row=1,sticky='EW')
        #Password label#
        
        #Password entry box
        self.PasswordEntry = Tkinter.Entry(self.f,textvariable=self.passwordEntry,show="*")
        self.PasswordEntry.grid(column=2,row=1,columnspan=2,sticky='EW')
        self.PasswordEntry.bind("<Return>", self.onPressEnterOnFields)
        #Password entry box
        
        #Login button
        self.button = Tkinter.Button(self.f,text=u"Login",command=self.OnButtonClick)
        self.button.grid(column=0,row=3,sticky='W',columnspan=3)
        #Login button
        
        #Status label
        self.Statuslabel = Tkinter.Label(self.f,textvariable=self.status,
                              anchor="e")
        self.Statuslabel.grid(column=0,row=4,columnspan=2)
        #Status label
        
        #Allow resizing
        self.grid_columnconfigure(0,weight=1)
        self.geometry("%dx%d%+d%+d" % (400, 100, 0, 0))
        
    def InitializeServerBrowser(self):
        
        self.f.grid()
        
        #Variable defintions
        self.topLabelText = Tkinter.StringVar()
        self.topLabelText.set("Logged in! (Your session ID is " + self.sessionID.get() + ")")
        self.addressLabelText = Tkinter.StringVar()
        self.addressLabelText.set("Server address:")
        self.address = Tkinter.StringVar()
        #Variable defintions
        
        #Top label
        topLabel = Tkinter.Label(self.f,textvariable=self.topLabelText,anchor="w")
        topLabel.grid(column=0,row=0,sticky='EW')
        #Top label
        
        #Address label
        addressLabel = Tkinter.Label(self.f,textvariable=self.addressLabelText,anchor="w")
        addressLabel.grid(column=0,row=1,sticky='EW')
        #Address lable
        
        #Address entry box
        self.AddressEntry = Tkinter.Entry(self.f,textvariable=self.address)
        self.AddressEntry.grid(column=1,row=1,columnspan=2,sticky='EW')
        #Address entry box
        
    def OnButtonClick(self):
        if(self.usernameEntry.get() == ""):
            self.status.set("Enter a username sherlock")
            return
        if(self.passwordEntry.get() == ""):
            self.status.set("Enter a password you derp")
            return
        password = self.passwordEntry.get()
        username = self.usernameEntry.get()
        self.status.set("Logging in.....")
        thread = MinecraftLoginThread(self, username, password)
        thread.start()
        thread.join()
        if(self.LoggedIn.get() == True):
            self.f.grid_forget()
            self.InitializeServerBrowser()
    
    def onPressEnterOnFields(self, event):
        if(self.usernameEntry.get() == ""):
            self.status.set("Enter a username sherlock")
            return
        if(self.passwordEntry.get() == ""):
            self.status.set("Enter a password you derp")
            return
        password = self.passwordEntry.get()
        username = self.usernameEntry.get()
        self.status.set("Logging in...")
        thread = MinecraftLoginThread(self, username, password)
        self.status.set("Logging in ....")
        thread.start()
        thread.join()
        if(self.LoggedIn.get() == True):
            self.f.grid_forget()
            self.InitializeServerBrowser()
        
class MinecraftLoginThread(threading.Thread):
    
    def __init__(self, window, username, password):
        threading.Thread.__init__(self)
        self.window = window
        self.username = username
        self.password = password
               
    def run(self):
        url = 'https://login.minecraft.net'
        header = {'Content-Type' : 'application/x-www-form-urlencoded'}
        data = {'user' : self.username, 
                'password' : self.password,
                'version' : '13'}
        data = urllib.urlencode(data)
        req = urllib2.Request(url, data, header)
        opener = urllib2.build_opener()
        response = opener.open(req)
        response = response.read()
        if(response == "Bad login"):
            self.window.status.set("Incorrect username or password!")
            return
        response = response.split(":")
        self.window.username.set(response[2])
        self.window.sessionID.set(response[3])
        self.window.LoggedIn.set(True)
        
if __name__ == "__main__":
    login = LoginWindow(None)
    login.title('pyCraft')
    login.mainloop()

"""
url = 'https://login.minecraft.net'
header = {'Content-Type' : 'application/x-www-form-urlencoded'}
username = raw_input("Enter your username: ")
password = getpass.getpass("Enter your password: ")
data = {'user' : username, 
        'password' : password,
        'version' : '13'}
data = urllib.urlencode(data)
req = urllib2.Request(url, data, header)
opener = urllib2.build_opener()
response = opener.open(req)
response = response.read()
response = response.split(":")
sessionid = response[3]
print "Your session id is: " + sessionid
mySocket = socket.socket ( socket.AF_INET, socket.SOCK_STREAM )
host = raw_input("Please enter host: ");
port = raw_input("Please enter port (return for 25565): ");
if(port == ""):
    port = 25565
else:
    port = int(port)
mySocket.connect ( ( host, port ) )
PacketManager.sendString("\x02", username + host + ":" + str(port), mySocket)
response = PacketManager.readStringFromSocket(mySocket)
print "Server id is: " + response['string']
serverid = response['string']
url = "http://session.minecraft.net/game/joinserver.jsp?user=" + username + "&sessionId=" + sessionid + "&serverId=" + serverid
response = urllib2.urlopen(url).read()
print "Response: " + response
if(response != "OK"):
    print "OH GOD RESPONSE IS NOT OK. QUITING NOW."
    sys.exit()
PacketManager.sendLoginRequest(mySocket, username)
while True:
    PacketManager.handleIncomingPacket(mySocket)
"""



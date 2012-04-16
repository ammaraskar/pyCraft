import wx
import start
import threading
import time

#pydev error fix
wx=wx

class LoginFrame(wx.Frame):
    
    def __init__(self, *args, **kwds):
        self.loggedIn = False
        
        # begin wxGlade: LoginFrame.__init__
        kwds["style"] = wx.CAPTION | wx.CLOSE_BOX | wx.MINIMIZE_BOX | wx.SYSTEM_MENU | wx.TAB_TRAVERSAL | wx.CLIP_CHILDREN
        wx.Frame.__init__(self, *args, **kwds)
        self.LoginStaticText = wx.StaticText(self, -1, "Login")
        self.static_line_1 = wx.StaticLine(self, -1)
        self.UsernameStaticText = wx.StaticText(self, -1, "Username")
        self.UsernameEntry = wx.TextCtrl(self, -1, "", style=wx.TE_PROCESS_ENTER)
        self.PasswordStaticText = wx.StaticText(self, -1, "Password")
        self.PasswordEntry = wx.TextCtrl(self, -1, "", style=wx.TE_PASSWORD | wx.TE_PROCESS_ENTER)
        self.LoginButton = wx.Button(self, -1, "&Login")
        self.static_line_2 = wx.StaticLine(self, -1)
        self.Status = wx.StaticText(self, -1, "pyCraft, python based minecraft client by Ammar Askar")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.handleLogin, self.LoginButton)
        self.UsernameEntry.Bind(wx.EVT_KEY_DOWN, self.onKeyDown)
        self.PasswordEntry.Bind(wx.EVT_KEY_DOWN, self.onKeyDown)
        # end wxGlade

    def __set_properties(self):
        # begin wxGlade: LoginFrame.__set_properties
        self.SetTitle("pyCraft")
        self.SetSize((500, 300))
        self.SetBackgroundColour(wx.Colour(171, 171, 171))
        self.SetFont(wx.Font(20, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        self.LoginStaticText.SetBackgroundColour(wx.Colour(171, 171, 171))
        self.LoginStaticText.SetFont(wx.Font(65, wx.MODERN, wx.NORMAL, wx.NORMAL, 0, "Minecraft"))
        self.UsernameStaticText.SetBackgroundColour(wx.Colour(171, 171, 171))
        self.UsernameStaticText.SetFont(wx.Font(14, wx.MODERN, wx.NORMAL, wx.NORMAL, 0, "Lucida Sans"))
        self.UsernameEntry.SetMinSize((150, 25))
        self.UsernameEntry.SetFont(wx.Font(12, wx.MODERN, wx.NORMAL, wx.NORMAL, 0, ""))
        self.PasswordStaticText.SetMinSize((87, 35))
        self.PasswordStaticText.SetBackgroundColour(wx.Colour(171, 171, 171))
        self.PasswordStaticText.SetFont(wx.Font(14, wx.MODERN, wx.NORMAL, wx.NORMAL, 0, "Lucida Sans"))
        self.PasswordEntry.SetMinSize((150, 25))
        self.PasswordEntry.SetFont(wx.Font(12, wx.MODERN, wx.NORMAL, wx.NORMAL, 0, ""))
        self.LoginButton.SetMinSize((80, 32))
        self.LoginButton.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_3DFACE))
        self.LoginButton.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        self.Status.SetBackgroundColour(wx.Colour(171, 171, 171))
        self.Status.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0))
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: LoginFrame.__do_layout
        sizer_5 = wx.BoxSizer(wx.VERTICAL)
        sizer_8 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_7 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_5.Add(self.LoginStaticText, 0, wx.LEFT | wx.TOP, 5)
        sizer_5.Add((20, 19), 0, 0, 0)
        sizer_5.Add((20, 48), 0, 0, 0)
        sizer_5.Add(self.static_line_1, 0, wx.EXPAND, 0)
        sizer_7.Add(self.UsernameStaticText, 0, wx.LEFT, 5)
        sizer_7.Add(self.UsernameEntry, 0, wx.LEFT, 15)
        sizer_5.Add(sizer_7, 1, wx.EXPAND, 0)
        sizer_8.Add(self.PasswordStaticText, 0, wx.LEFT, 5)
        sizer_8.Add(self.PasswordEntry, 0, wx.LEFT, 20)
        sizer_8.Add(self.LoginButton, 0, wx.LEFT, 145)
        sizer_5.Add(sizer_8, 1, wx.EXPAND, 0)
        sizer_5.Add(self.static_line_2, 0, wx.EXPAND, 0)
        sizer_5.Add(self.Status, 0, wx.LEFT, 5)
        self.SetSizer(sizer_5)
        self.Layout()
        self.Centre()
        # end wxGlade
        
    def onKeyDown(self, event):
        if(event.GetKeyCode() == 9):
            if(event.GetEventObject() == self.UsernameEntry):
                self.PasswordEntry.SetFocus()
            if(event.GetEventObject() == self.PasswordEntry):
                self.UsernameEntry.SetFocus()
        else:
            event.Skip()

    def handlePostLogin(self, threadtokill):
        threadtokill.Kill = True
        self.Status.SetLabel("Logged in!") #For now just sets label to logged in, will call new frame in the future
        pass
    
    def handleEnter(self):
        print "mebbe this works"
        
    def handleLogin(self, event):
        if(self.UsernameEntry.GetValue() == ""):
            self.Status.SetForegroundColour(wx.RED)
            self.Status.SetLabel("Enter a username")
            return
        if(self.PasswordEntry.GetValue() == ""):
            self.Status.SetForegroundColour(wx.RED)
            self.Status.SetLabel("Enter a password")
            return
        username = self.UsernameEntry.GetValue()
        password = self.PasswordEntry.GetValue()
        self.Status.SetForegroundColour(wx.BLUE)
        self.Status.SetLabel("Connecting.")
        RotationThread = ConnectingRotationThread(self)
        RotationThread.start()
        LoginThread = start.MinecraftLoginThread(self, RotationThread, username, password)
        LoginThread.start()
        
class ConnectingRotationThread(threading.Thread):
    
    def __init__(self, window):
        threading.Thread.__init__(self)
        self.window = window 
        self.Kill = False
    
    def run(self):
        i = 1
        while True:
            if(self.Kill == True):
                break
            if(i == 0):
                self.window.Status.SetLabel("Connecting.")
            if(i == 1):
                self.window.Status.SetLabel("Connecting..")
            if(i == 2):
                self.window.Status.SetLabel("Connecting...")
            if(i == 3):
                self.window.Status.SetLabel("Connecting....")
            if(i == 4):
                self.window.Status.SetLabel("Connecting.....")
                i = -1
            i = i + 1
            time.sleep(1)
        
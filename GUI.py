import wx
import wx.lib.scrolledpanel as scrolled
import wx.richtext as rt
import start
import threading
import time
import NetworkManager

#pydev error fix
wx=wx

class MainFrame(wx.Frame):
    
    def __init__(self, *args, **kwds):
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        
        self.Freeze()
        self.LoginPanel = LoginFrame(self)
        self.ConnectPanel = ServerPanel(self)
        self.ConnectPanel.Hide()
        self.ChatPanel = ServerChatPanel(self)
        self.ChatPanel.Hide()
        self.LoginPanel.Show()
        self.SetSize((520, 310))
        self.SetTitle("pyCraft")
        self.Thaw()
        
    def setOutGoingSocket(self, socket):
        self.socket = socket
        
    def showConnectionPanel(self):
        self.LoginPanel.Hide()
        self.SetMinSize((600, 310))
        self.SetSize((600, 310))
        self.ConnectPanel.Show()
        self.Layout()
        self.ConnectPanel.Layout()
        
    def showChatPanel(self):
        self.ChatPanel.Hide()
        self.ConnectPanel.Hide()
        self.LoginPanel.Hide()
        self.SetSize((600, 450))
        self.SetMinSize((600, 450))
        self.ChatPanel.Show()
        self.Layout()
        self.ChatPanel.Layout()

class LoginFrame(wx.Panel):
    
    def __init__(self, parent):
        
        # begin wxGlade: LoginFrame.__init__
        wx.Panel.__init__(self, parent)
        self.parent = parent
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
        self.UsernameEntry.Bind(wx.EVT_TEXT_ENTER, self.handleLogin)
        self.PasswordEntry.Bind(wx.EVT_TEXT_ENTER, self.handleLogin)
        self.UsernameEntry.Bind(wx.EVT_KEY_DOWN, self.onKeyDown)
        self.PasswordEntry.Bind(wx.EVT_KEY_DOWN, self.onKeyDown)
        # end wxGlade

    def __set_properties(self):
        # begin wxGlade: LoginFrame.__set_properties
        self.parent.SetSize((520, 310))
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
        self.Status.SetLabel("Logged in!")
        self.parent.showConnectionPanel()
        
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
        
class ServerPanel(wx.Panel):
    
    def __init__(self, parent):
        # begin wxGlade: ServerConnectFrame.__init__
        wx.Panel.__init__(self, parent=parent)
        
        self.parent = parent
        
        self.Status = wx.StaticText(self, -1, "")
        self.ServerAddressStaticText = wx.StaticText(self, -1, "Server Address")
        self.ServerAddressInput = wx.TextCtrl(self, -1, "", style=wx.TE_PROCESS_ENTER)
        self.ConnectButton = wx.Button(self, -1, "&Connect")
        self.NoGraphicsCheck = wx.CheckBox(self, -1, "")
        self.NoGraphicsStaticText = wx.StaticText(self, -1, "No Graphics (Stub until I implement graphics)")

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.onConnect, self.ConnectButton)
        self.Bind(wx.EVT_TEXT_ENTER, self.onConnect, self.ServerAddressInput)
        # end wxGlade

    def __set_properties(self):
        # begin wxGlade: ServerConnectFrame.__set_properties
        self.SetSize((605, 405))
        self.SetBackgroundColour(wx.Colour(171, 171, 171))
        self.Status.SetBackgroundColour(wx.Colour(171, 171, 171))
        self.Status.SetFont(wx.Font(25, wx.MODERN, wx.NORMAL, wx.NORMAL, 0, "Minecraft"))
        self.ServerAddressStaticText.SetBackgroundColour(wx.Colour(171, 171, 171))
        self.ServerAddressStaticText.SetFont(wx.Font(12, wx.MODERN, wx.NORMAL, wx.NORMAL, 0, "Minecraft"))
        self.ServerAddressInput.SetMinSize((200, 25))
        self.ServerAddressInput.SetFont(wx.Font(11, wx.MODERN, wx.NORMAL, wx.NORMAL, 0, "Minecraft"))
        self.ConnectButton.SetMinSize((125, 25))
        self.ConnectButton.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_3DFACE))
        self.NoGraphicsCheck.SetMinSize((13, 13))
        self.NoGraphicsCheck.SetBackgroundColour(wx.Colour(171, 171, 171))
        self.NoGraphicsCheck.Enable(False)
        self.NoGraphicsCheck.SetValue(1)
        self.NoGraphicsStaticText.SetBackgroundColour(wx.Colour(171, 171, 171))
        self.NoGraphicsStaticText.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: ServerConnectFrame.__do_layout
        self.sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_3 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer_1.Add(self.Status, 0, wx.LEFT, 5)
        self.sizer_1.Add((20, 45), 0, 0, 0)
        sizer_2.Add(self.ServerAddressStaticText, 0, wx.LEFT, 5)
        sizer_2.Add(self.ServerAddressInput, 0, wx.LEFT, 15)
        sizer_2.Add(self.ConnectButton, 0, wx.LEFT, 15)
        self.sizer_1.Add(sizer_2, 1, 0, 0)
        sizer_3.Add(self.NoGraphicsCheck, 0, wx.LEFT | wx.TOP, 5)
        sizer_3.Add(self.NoGraphicsStaticText, 0, wx.LEFT, 10)
        self.sizer_1.Add(sizer_3, 1, wx.EXPAND, 0)
        self.SetSizer(self.sizer_1)
        # end wxGlade
        
    def onConnect(self, event):
        StuffEnteredIntoBox = self.ServerAddressInput.GetValue().split(":")
        host = StuffEnteredIntoBox[0]
        if(len(StuffEnteredIntoBox) > 1):
            port = int(StuffEnteredIntoBox[1])
        else:
            port = 25565
        connection = NetworkManager.ServerConnection(self.parent, self.parent.username, "", self.parent.sessionID, host, port)
        connection.start() 
        self.Status.SetLabel("Connecting.")
        self.RotationThread = ConnectingRotationThread(self)
        self.RotationThread.start()
    
    def callbackAfterConnect(self):
        self.RotationThread.Kill = True
        self.parent.showChatPanel()
        
class ServerChatPanel(wx.Panel):
    
    def __init__(self, parent):
        # begin wxGlade: wxScrolledPanel.__init__
        wx.Panel.__init__(self, parent=parent)
        
        self.parent = parent
        
        self.Status = wx.StaticText(self, -1, "HERP DERP TEST STUFF")
        self.messageEntry = wx.TextCtrl(self, -1, "", style=wx.EXPAND|wx.TE_PROCESS_ENTER)
        self.messageEntry.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        self.sendButton = wx.Button(self, -1, "&Send", size=(100, wx.Button.GetDefaultSize()[1]))
        self.sendButton.SetMinSize((100, wx.Button.GetDefaultSize()[1]))
        self.sendButton.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_3DFACE))
        """
        self.ChatPanel = scrolled.ScrolledPanel(self, 1, size=(self.parent.GetSize()[0], self.parent.GetSize()[1] - 40),
                                 style = wx.TAB_TRAVERSAL|wx.SUNKEN_BORDER|wx.EXPAND|wx.ALL, name="ChatPanel" )
        self.ChatPanelSizer = wx.BoxSizer(wx.VERTICAL)
        """
        
        self.__set_properties()
        self.__do_layout()
        
        self.locked = True
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_ICONIZE, self.OnPaint)
        self.text.Bind(wx.EVT_SCROLLWIN, self.OnScroll)
        self.messageEntry.Bind(wx.EVT_TEXT_ENTER, self.sendMessage)
        
        self.SetAutoLayout(True)
        self.text.BeginFontSize(12)
        self.text.Scroll(0, self.text.GetScrollRange(wx.VERTICAL)) 
        # end wxGlade

    def __set_properties(self):
        # begin wxGlade: ServerConnectionPanel.__set_properties
        self.SetBackgroundColour(wx.Colour(171, 171, 171))
        self.Status.SetBackgroundColour(wx.Colour(171, 171, 171))
        self.Status.SetFont(wx.Font(14, wx.MODERN, wx.NORMAL, wx.BOLD, 0, "Minecraft"))
        #self.ChatPanel.SetupScrolling()
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: ServerConnectionPanel.__do_layout
        self.SetSizeHints(-1,self.GetSize().y,-1,self.GetSize().y );
        self.RootSizer = wx.BoxSizer(wx.VERTICAL)
        #sizer_4 = wx.BoxSizer(wx.VERTICAL)
        self.sizer_6 = wx.BoxSizer(wx.HORIZONTAL)
        self.RootSizer.Add(self.Status, 0, wx.LEFT, 6)
        #self.RootSizer.Add(self.ChatPanel, 1, wx.EXPAND|wx.ALL)
        self.hbox5 = wx.BoxSizer(wx.HORIZONTAL) 
        self.text = rt.RichTextCtrl(self, 1, style=wx.VSCROLL|wx.EXPAND|wx.SUNKEN_BORDER|wx.ALL, size=(self.parent.GetSize()[0] - 20, self.parent.GetSize()[1] - 100)) 
        self.RootSizer.Add(self.text, 1, wx.ALL|wx.EXPAND, 3)
        self.RootSizer.Fit(self)
        self.RootSizer.Add(self.sizer_6, 0, wx.EXPAND, 0)
        self.sizer_6.Add(self.messageEntry, 1, wx.EXPAND|wx.ALL, 3)
        self.sizer_6.Add(self.sendButton, 0, wx.EXPAND|wx.ALL, 3)
        #self.RootSizer.Add(sizer_4, 1, wx.EXPAND, 0)
        self.SetSizer(self.RootSizer)
        self.RootSizer.Fit(self)
        self.Layout()
        # end wxGlade
        
    def OnScroll(self, event):
        event.Skip()
        if(self.text.GetScrollRange(wx.VERTICAL) - self.text.GetScrollPos(wx.VERTICAL) == 81):
            self.locked = True
        else:
            self.locked = False
            
    def OnPaint(self, event):
        self.text.SetSize((self.parent.GetSize()[0] - 20, self.parent.GetSize()[1] - 100))
        if(self.locked):
            self.text.Scroll(0, self.text.GetScrollRange(wx.VERTICAL))
        wx.PaintDC(self)          
    
    def sendMessage(self, event):
        if(self.messageEntry.GetValue() == ""):
            self.Status.SetLabel("No message entered QQ")
        
    def handleChat(self, message):
        pass
    
# end of class wxScrolledPanel

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
            if(i == 0 and self.window):
                self.window.Status.SetLabel("Connecting.")
            elif(i == 1 and self.window):
                self.window.Status.SetLabel("Connecting..")
            elif(i == 2 and self.window):
                self.window.Status.SetLabel("Connecting...")
            elif(i == 3 and self.window):
                self.window.Status.SetLabel("Connecting....")
            elif(i == 4 and self.window):
                self.window.Status.SetLabel("Connecting.....")
                i = -1
            elif(self.window == None):
                self.Kill = True
            i = i + 1
            time.sleep(1)
        
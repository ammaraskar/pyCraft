import socket
import PacketListenerManager
import urllib2
import urllib
import traceback
import threading
import hashlib
import string
import Utils
from networking import PacketSenderManager
from Crypto.Random import _UserFriendlyRNG
from Crypto.Util import asn1
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES
from Crypto.Cipher import PKCS1_v1_5
try:
    import wx
    #Eclipse pyDev error fix
    wx=wx
except ImportError:
    pass

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
        try:
            #Create the socket and fileobject
            self.socket = socket.socket ( socket.AF_INET, socket.SOCK_STREAM )
            self.socket.connect ( ( self.server, self.port ) )
            self.FileObject = self.socket.makefile()
            
            #Send out the handshake packet
            PacketSenderManager.sendHandshake(self.socket, self.username, self.server, self.port)
            
            #Receive the encryption packet id
            packetid = self.socket.recv(1)
            
            #Sanity check the packet id
            if (packetid != "\xFD"):
                if(self.NoGUI == False):
                    self.window.ConnectPanel.Status.SetFont(wx.Font(15, wx.MODERN, wx.NORMAL, wx.NORMAL, 0, "Minecraft"))
                    self.window.ConnectPanel.Status.SetLabel("Server responded with malformed packet")
                else:
                    print "Server responded with malformed packet"
                    return False
                
            #Parse the packet
            packetFD = PacketListenerManager.handleFD(self.FileObject)
            
            #Import the server's public key
            self.pubkey = RSA.importKey(packetFD['Public Key'])
            
            #Generate a 16 byte (128 bit) shared secret
            self.sharedSecret = _UserFriendlyRNG.get_random_bytes(16)
            
            #Grab the server id
            sha1 = hashlib.sha1()
            sha1.update(packetFD['ServerID'])
            sha1.update(self.sharedSecret)
            sha1.update(packetFD['Public Key'])
            #lovely java style hex digest by SirCmpwn
            sha1 = sha1.hexdigest()
            negative = (int(sha1[0], 16) & 0x80) == 0x80
            if(negative):
                sha1 = Utils.TwosCompliment(sha1.digest())
            #else:
            #    sha1 = sha1.digest()
            Utils.trimStart(str(sha1), '0')
            if (negative):
                sha1 = '-' + sha1
            serverid = sha1
            
            #Authenticate the server from sessions.minecraft.net
            if(serverid != '-'):
                try:
                    #Open up the url with the appropriate get parameters
                    url = "http://session.minecraft.net/game/joinserver.jsp?user=" + self.username + "&sessionId=" + self.sessionID + "&serverId=" + serverid
                    response = urllib2.urlopen(url).read()
                    
                    if(response != "OK"):
                        #handle gui errors
                        if(self.NoGUI == False):
                            self.window.ConnectPanel.Status.SetFont(wx.Font(15, wx.MODERN, wx.NORMAL, wx.NORMAL, 0, "Minecraft"))
                            self.window.ConnectPanel.Status.SetLabel("Response from sessions.minecraft.net wasn't OK")
                        else:
                            print "Response from sessions.minecraft.net wasn't OK, it was " + response
                            return False
                        
                    #Success \o/ We can now begin sending our stuff to the server
                    
                    #Instantiate our main packet listener
                    PacketListener(self, self.window, self.socket, self.FileObject).start()
                    
                    #Encrypt the verification token from earlier along with our shared secret with the server's rsa key
                    self.RSACipher = PKCS1_v1_5.new(self.pubkey)
                    encryptedSanityToken = self.RSACipher.encrypt(str(packetFD['Token']))
                    encryptedSharedSecret = self.RSACipher.encrypt(str(self.sharedSecret))
                    
                    #Send out a a packet FC to the server
                    PacketSenderManager.sendFC(self.socket, encryptedSharedSecret, encryptedSanityToken)
                    
                    #GUI handling
                    if(self.NoGUI == False):
                        self.window.ConnectPanel.callbackAfterConnect()
                        #Wait for server screen to be ready
                        while(not hasattr(self.window, 'text')):
                            continue
                        
                except Exception, e:
                    #handle gui errors
                    if(self.NoGUI == False and hasattr(self.window, 'ConnectPanel')):
                        self.window.ConnectPanel.Status.SetForegroundColour(wx.RED)
                        self.window.ConnectPanel.Status.SetLabel("Conection to sessions.mc.net failed")
                        self.window.ConnectPanel.RotationThread.Kill = True
                    traceback.print_exc()
            else:
                if(self.NoGUI):
                    print "Server is in offline mode"
                #TODO: handle offline mod servers
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
        
class EncryptedFileObjectHandler():
    
    def __init__(self, fileobject, cipher):
        self.fileobject = fileobject
        self.cipher = cipher
        
    def read(self, length):
        rawData = self.fileobject.read(length)
        unencryptedData = self.cipher.decrypt(rawData)
        return unencryptedData
    
class EncryptedSocketObjectHandler():
    
    def __init__(self, socket, cipher):
        self.socket = socket
        self.cipher = cipher
    
    def send(self, stuff):
        self.socket.send(self.cipher.encrypt(stuff))
    
    def close(self):
        self.socket.close()
                
class PacketListener(threading.Thread):
    
    def __init__(self, connection, window, socket, FileObject):
        threading.Thread.__init__(self)
        self.connection = connection
        self.socket = socket
        self.FileObject = FileObject
        self.window = window
        self.encryptedConnection = False
        
    def enableEncryption(self):
        #Create an AES cipher from the previously obtained public key
        self.cipher = AES.new(self.connection.sharedSecret, AES.MODE_CFB, IV=self.connection.sharedSecret)
        self.decipher = AES.new(self.connection.sharedSecret, AES.MODE_CFB, IV=self.connection.sharedSecret)
        self.rawsocket = self.socket
        self.socket = EncryptedSocketObjectHandler(self.rawsocket, self.cipher)
        self.rawFileObject = self.FileObject
        self.FileObject = EncryptedFileObjectHandler(self.rawFileObject, self.decipher)
        self.encryptedConnection = True
        
    def run(self):
        while True:
            try:
                response = self.FileObject.read(1)
                if (response == ""):
                    continue
            except Exception, e:
                if(self.window):
                    self.window.Status.SetLabel("Ping timeout")
                else:
                    print "Ping timeout"
                    traceback.print_exc()
                break
            if(response == "\x00"):
                PacketListenerManager.handle00(self.FileObject, self.socket)
            elif(response == "\x01"):
                packet01 = PacketListenerManager.handle01(self.FileObject)
                print "Logged in \o/ Received an entity id of " + str(packet01['EntityID'])
            elif(response == "\x03"):
                message = PacketListenerManager.handle03(self.FileObject)
                if(self.connection.NoGUI):
                    filtered_string = filter(lambda x: x in string.printable, message)
                    #print message.replace(u'\xa7', '&')
                    print filtered_string
                elif(self.window):
                    self.window.handleChat(message)
            elif(response == "\x04"):
                PacketListenerManager.handle04(self.FileObject)
            elif(response == "\x05"):
                PacketListenerManager.handle05(self.FileObject)
            elif(response == "\x06"):
                PacketListenerManager.handle06(self.FileObject)
            elif(response == "\x07"):
                PacketListenerManager.handle07(self.FileObject)
            elif(response == "\x08"):
                PacketListenerManager.handle08(self.FileObject)
            elif(response == "\x09"):
                PacketListenerManager.handle09(self.FileObject)
            elif(response == "\x0D"):
                PacketListenerManager.handle0D(self.FileObject)
            elif(response == "\x11"):
                PacketListenerManager.handle11(self.FileObject)
            elif(response == "\x12"):
                PacketListenerManager.handle12(self.FileObject)
            elif(response == "\x14"):
                PacketListenerManager.handle14(self.FileObject)
            elif(response == "\x15"):
                PacketListenerManager.handle15(self.FileObject)
            elif(response == "\x16"):
                PacketListenerManager.handle16(self.FileObject)
            elif(response == "\x17"):
                PacketListenerManager.handle17(self.FileObject)
            elif(response == "\x18"):
                PacketListenerManager.handle18(self.FileObject)
            elif(response == "\x19"):
                PacketListenerManager.handle19(self.FileObject)
            elif(response == "\x1A"):
                PacketListenerManager.handle1A(self.FileObject)
            elif(response == "\x1C"):
                PacketListenerManager.handle1C(self.FileObject)
            elif(response == "\x1D"):
                PacketListenerManager.handle1D(self.FileObject)
            elif(response == "\x1E"):
                PacketListenerManager.handle1E(self.FileObject)
            elif(response == "\x1F"):
                PacketListenerManager.handle1F(self.FileObject)
            elif(response == "\x20"):
                PacketListenerManager.handle20(self.FileObject)
            elif(response == "\x21"):
                PacketListenerManager.handle21(self.FileObject)
            elif(response == "\x22"):
                PacketListenerManager.handle22(self.FileObject)
            elif(response == "\x23"):
                PacketListenerManager.handle23(self.FileObject)
            elif(response == "\x26"):
                PacketListenerManager.handle26(self.FileObject)
            elif(response == "\x27"):
                PacketListenerManager.handle27(self.FileObject)
            elif(response == "\x28"):
                PacketListenerManager.handle28(self.FileObject)
            elif(response == "\x29"):
                PacketListenerManager.handle29(self.FileObject)
            elif(response == "\x2A"):
                PacketListenerManager.handle2A(self.FileObject)
            elif(response == "\x2B"): 
                PacketListenerManager.handle2B(self.FileObject)
            elif(response == "\x33"):
                PacketListenerManager.handle33(self.FileObject)
            elif(response == "\x34"):
                PacketListenerManager.handle34(self.FileObject)
            elif(response == "\x35"):
                PacketListenerManager.handle35(self.FileObject)
            elif(response == "\x36"):
                PacketListenerManager.handle36(self.FileObject)
            elif(response == "\x37"):
                PacketListenerManager.handle37(self.FileObject)
            elif(response == "\x38"):
                PacketListenerManager.handle38(self.FileObject)
            elif(response == "\x3C"):
                PacketListenerManager.handle3C(self.FileObject)
            elif(response == "\x3D"):
                PacketListenerManager.handle3D(self.FileObject)
            elif(response == "\x3E"):
                PacketListenerManager.handle3E(self.FileObject)
            elif(response == "\x46"):
                PacketListenerManager.handle46(self.FileObject)
            elif(response == "\x47"):
                PacketListenerManager.handle47(self.FileObject)
            elif(response == "\x64"):
                PacketListenerManager.handle64(self.FileObject)
            elif(response == "\x65"):
                PacketListenerManager.handle65(self.FileObject)
            elif(response == "\x67"):
                PacketListenerManager.handle67(self.FileObject)
            elif(response == "\x68"):
                PacketListenerManager.handle68(self.FileObject)
            elif(response == "\x69"):
                PacketListenerManager.handle69(self.FileObject)
            elif(response == "\x6A"):
                PacketListenerManager.handle6A(self.FileObject)
            elif(response == "\x6B"):
                PacketListenerManager.handle6B(self.FileObject)
            elif(response == "\x82"):
                PacketListenerManager.handle82(self.FileObject)
            elif(response == "\x83"):
                PacketListenerManager.handle83(self.FileObject)
            elif(response == "\x84"):
                PacketListenerManager.handle84(self.FileObject)
            elif(response == "\xC8"):
                PacketListenerManager.handleC8(self.FileObject)
            elif(response == "\xC9"):
                PacketListenerManager.handleC9(self.FileObject)
            elif(response == "\xCA"):
                PacketListenerManager.handleCA(self.FileObject)
            elif(response == "\xCB"):
                PacketListenerManager.handleCB(self.FileObject)
            elif(response == "\xFA"):
                PacketListenerManager.handleFA(self.FileObject)
            elif(response == "\xFC"):
                PacketListenerManager.handleFC(self.FileObject)
                if (not self.encryptedConnection):
                    self.enableEncryption()
                    PacketSenderManager.sendCD(self.socket, 0)
            elif(response == "\xFF"):
                DisconMessage = PacketListenerManager.handleFF(self.FileObject)
                if(self.window == None):
                    print "Disconnected: " + DisconMessage
                if(self.window):
                    if(hasattr(self.window, 'ChatPanel')):
                        self.window.ChatPanel.Status.SetLabel("Disconnected: " + DisconMessage)
                    if(hasattr(self.window, 'Status')):
                        self.window.Status.SetLabel("Disconnected: " + DisconMessage)
                self.socket.close()
                break
            else:
                if(self.window == None):
                    print "Protocol error: " + hex(ord(response))
                    self.socket.close()
                    break
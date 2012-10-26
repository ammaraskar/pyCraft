import socket
import PacketListenerManager
import urllib2
import traceback
import threading
import hashlib
import string
import Utils
import sys
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
    
    def __init__(self, window, username, password, sessionID, server, port, options=None):
        threading.Thread.__init__(self)
        self.options = options
        self.isConnected = False
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
        
    def disconnect(self, reason="Disconnected by user"):
        PacketSenderManager.sendFF(self.socket, reason)
        self.listener.kill = True
        self.socket.close()
        
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
            assert packetid == "\xFD", "Server didn't respond back to handshake with proper packet!"
                
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
            #lovely java style hex digest by barneygale
            serverid = Utils.javaHexDigest(sha1)
            
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
                    self.listener = PacketListener(self, self.window, self.socket, self.FileObject)
                    self.listener.start()
                    
                    #Encrypt the verification token from earlier along with our shared secret with the server's rsa key
                    self.RSACipher = PKCS1_v1_5.new(self.pubkey)
                    encryptedSanityToken = self.RSACipher.encrypt(str(packetFD['Token']))
                    encryptedSharedSecret = self.RSACipher.encrypt(str(self.sharedSecret))
                    
                    #Send out a a packet FC to the server
                    PacketSenderManager.sendFC(self.socket, encryptedSharedSecret, encryptedSanityToken)
                        
                except Exception, e:
                    traceback.print_exc()
            else:
                print "Server is in offline mode"
                #TODO: handle offline mod servers
        except Exception, e:
            print "Connection to server failed"
            traceback.print_exc()
            sys.exit(1)
            return False
        
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
        self.kill = False
        
    def enableEncryption(self):
        #Create an AES cipher from the previously obtained public key
        self.cipher = AES.new(self.connection.sharedSecret, AES.MODE_CFB, IV=self.connection.sharedSecret)
        self.decipher = AES.new(self.connection.sharedSecret, AES.MODE_CFB, IV=self.connection.sharedSecret)
        
        self.rawsocket = self.socket
        self.connection.rawsocket = self.connection.socket
        self.socket = EncryptedSocketObjectHandler(self.rawsocket, self.cipher)
        self.connection.socket = self.socket
        
        self.rawFileObject = self.FileObject
        self.connection.rawFileObject = self.connection.FileObject
        self.FileObject = EncryptedFileObjectHandler(self.rawFileObject, self.decipher)
        self.connection.FileObject = self.FileObject
        
        self.encryptedConnection = True
        
    def run(self):
        
        if(self.connection.options != None and self.connection.options.dumpPackets):
            f = open(self.connection.options.filename, 'w')
        while True:
            if (self.kill):
                break
            try:
                response = self.FileObject.read(1)
                if (response == ""):
                    continue
            except Exception, e:
                if(self.window):
                    self.window.Status.SetLabel("Ping timeout")
                else:
                    print "Ping timeout"
                    sys.exit()
                break
            if(response == "\x00"):
                packet = PacketListenerManager.handle00(self.FileObject, self.socket)
            elif(response == "\x01"):
                packet = PacketListenerManager.handle01(self.FileObject)
                print "Logged in \o/ Received an entity id of " + str(packet['EntityID'])
            elif(response == "\x03"):
                packet = PacketListenerManager.handle03(self.FileObject)
                # Add "\x1b" because it is essential for ANSI escapes emitted by translate_escapes
                filtered_string = filter(lambda x: x in string.printable + "\x1b", Utils.translate_escapes(packet['Message']))
                #print message.replace(u'\xa7', '&')
                print filtered_string
                packet['Message'] = filter(lambda x: x in string.printable, packet['Message'])
            elif(response == "\x04"):
                packet = PacketListenerManager.handle04(self.FileObject)
            elif(response == "\x05"):
                packet = PacketListenerManager.handle05(self.FileObject)
            elif(response == "\x06"):
                packet = PacketListenerManager.handle06(self.FileObject)
            elif(response == "\x07"):
                packet = PacketListenerManager.handle07(self.FileObject)
            elif(response == "\x08"):
                packet = PacketListenerManager.handle08(self.FileObject)
            elif(response == "\x09"):
                packet = PacketListenerManager.handle09(self.FileObject)
            elif(response == "\x0D"):
                packet = PacketListenerManager.handle0D(self.FileObject)
            elif(response == "\x11"):
                packet = PacketListenerManager.handle11(self.FileObject)
            elif(response == "\x12"):
                packet = PacketListenerManager.handle12(self.FileObject)
            elif(response == "\x14"):
                packet = PacketListenerManager.handle14(self.FileObject)
            elif(response == "\x15"):
                packet = PacketListenerManager.handle15(self.FileObject)
            elif(response == "\x16"):
                packet = PacketListenerManager.handle16(self.FileObject)
            elif(response == "\x17"):
                packet = PacketListenerManager.handle17(self.FileObject)
            elif(response == "\x18"):
                packet = PacketListenerManager.handle18(self.FileObject)
            elif(response == "\x19"):
                packet = PacketListenerManager.handle19(self.FileObject)
            elif(response == "\x1A"):
                packet = PacketListenerManager.handle1A(self.FileObject)
            elif(response == "\x1C"):
                packet = PacketListenerManager.handle1C(self.FileObject)
            elif(response == "\x1D"):
                packet = PacketListenerManager.handle1D(self.FileObject)
            elif(response == "\x1E"):
                packet = PacketListenerManager.handle1E(self.FileObject)
            elif(response == "\x1F"):
                packet = PacketListenerManager.handle1F(self.FileObject)
            elif(response == "\x20"):
                packet = PacketListenerManager.handle20(self.FileObject)
            elif(response == "\x21"):
                packet = PacketListenerManager.handle21(self.FileObject)
            elif(response == "\x22"):
                packet = PacketListenerManager.handle22(self.FileObject)
            elif(response == "\x23"):
                packet = PacketListenerManager.handle23(self.FileObject)
            elif(response == "\x26"):
                packet = PacketListenerManager.handle26(self.FileObject)
            elif(response == "\x27"):
                packet = PacketListenerManager.handle27(self.FileObject)
            elif(response == "\x28"):
                packet = PacketListenerManager.handle28(self.FileObject)
            elif(response == "\x29"):
                packet = PacketListenerManager.handle29(self.FileObject)
            elif(response == "\x2A"):
                packet = PacketListenerManager.handle2A(self.FileObject)
            elif(response == "\x2B"): 
                packet = PacketListenerManager.handle2B(self.FileObject)
            elif(response == "\x33"):
                PacketListenerManager.handle33(self.FileObject)
                packet = {'ChunkPlaceHolder' : 0}
            elif(response == "\x34"):
                packet = PacketListenerManager.handle34(self.FileObject)
            elif(response == "\x35"):
                packet = PacketListenerManager.handle35(self.FileObject)
            elif(response == "\x36"):
                packet = PacketListenerManager.handle36(self.FileObject)
            elif(response == "\x37"):
                packet = PacketListenerManager.handle37(self.FileObject)
            elif(response == "\x38"):
                PacketListenerManager.handle38(self.FileObject)
                packet = {'ChunkPlaceHolder' : 0}
            elif(response == "\x3C"):
                packet = PacketListenerManager.handle3C(self.FileObject)
            elif(response == "\x3D"):
                packet = PacketListenerManager.handle3D(self.FileObject)
            elif(response == "\x3E"):
                packet = PacketListenerManager.handle3E(self.FileObject)
            elif(response == "\x46"):
                packet = PacketListenerManager.handle46(self.FileObject)
            elif(response == "\x47"):
                packet = PacketListenerManager.handle47(self.FileObject)
            elif(response == "\x64"):
                packet = PacketListenerManager.handle64(self.FileObject)
            elif(response == "\x65"):
                packet = PacketListenerManager.handle65(self.FileObject)
            elif(response == "\x67"):
                packet = PacketListenerManager.handle67(self.FileObject)
            elif(response == "\x68"):
                packet = PacketListenerManager.handle68(self.FileObject)
            elif(response == "\x69"):
                packet = PacketListenerManager.handle69(self.FileObject)
            elif(response == "\x6A"):
                packet = PacketListenerManager.handle6A(self.FileObject)
            elif(response == "\x6B"):
                packet = PacketListenerManager.handle6B(self.FileObject)
            elif(response == "\x82"):
                packet = PacketListenerManager.handle82(self.FileObject)
            elif(response == "\x83"):
                packet = PacketListenerManager.handle83(self.FileObject)
            elif(response == "\x84"):
                packet = PacketListenerManager.handle84(self.FileObject)
            elif(response == "\xC8"):
                packet = PacketListenerManager.handleC8(self.FileObject)
            elif(response == "\xC9"):
                packet = PacketListenerManager.handleC9(self.FileObject)
            elif(response == "\xCA"):
                packet = PacketListenerManager.handleCA(self.FileObject)
            elif(response == "\xCB"):
                packet = PacketListenerManager.handleCB(self.FileObject)
            elif(response == "\xFA"):
                packet = PacketListenerManager.handleFA(self.FileObject)
            elif(response == "\xFC"):
                packet = PacketListenerManager.handleFC(self.FileObject)
                if (not self.encryptedConnection):
                    self.enableEncryption()
                    self.connection.isConnected = True
                    PacketSenderManager.sendCD(self.socket, 0)
            elif(response == "\xFF"):
                packet = PacketListenerManager.handleFF(self.FileObject)
                print "Disconnected: " + packet['Reason']
                if(self.connection.options != None and self.connection.options.dumpPackets):
                    f.close()
                self.connection.disconnect()
                sys.exit(1)
                break
            else:
                print "Protocol error: " + hex(ord(response))
                self.connection.disconnect("Protocol error, invalid packet: " + hex(ord(response)))
                if(f != None):
                    f.close()
                sys.exit(1)
                break
            if(self.connection.options != None and self.connection.options.dumpPackets):
                f.write(hex(ord(response)) + " : " + str(packet) + '\n')
